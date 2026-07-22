from backend.models.base import EntityId
from repositories.base import BaseRepository
from psycopg import AsyncConnection
from datetime import datetime
from typing import Literal
from models.sales import SalesSummary, TimeSeriesPoint, EventSalesSummary, TierSalesSummary
from models import Event, EventTier


class SalesRepository(BaseRepository):
    def __init__(self, db_session: AsyncConnection):
        super().__init__(db_session)

    async def get_sales_summary(self, start_date: datetime, end_date: datetime) -> SalesSummary | None:
        async with self.db_session.cursor() as cursor:
            await cursor.execute("""
                SELECT
                    COALESCE(SUM(total_price) FILTER (WHERE status = 'confirmed'), 0) AS confirmed_revenue,
                    COALESCE(SUM(total_price) FILTER (WHERE status IN ('expired', 'cancelled')), 0) AS lost_revenue,
                    COUNT(*) FILTER (WHERE status = 'confirmed') AS confirmed_bookings_count,
                    COALESCE(SUM(ticket_count) FILTER (WHERE status = 'confirmed'), 0) AS sold_tickets
                FROM bookings
                WHERE created_at >= %s AND created_at < %s
            """, (start_date, end_date))
            
            row = await cursor.fetchone()
            if not row:
                return None
            
            return SalesSummary(
                confirmed_revenue=float(row['confirmed_revenue']),
                lost_revenue=float(row['lost_revenue']),
                confirmed_bookings_count=int(row['confirmed_bookings_count']),
                sold_tickets=int(row['sold_tickets'])
            )

    async def get_sales_over_time(
        self, 
        start_date: datetime, 
        end_date: datetime, 
        granularity: Literal['day', 'week', 'month'] = 'day'
    ) -> list[TimeSeriesPoint]:
        async with self.db_session.cursor() as cursor:
            await cursor.execute("""
                SELECT
                    date_trunc(%s, created_at) AS period,
                    SUM(total_price) AS revenue,
                    SUM(ticket_count) AS tickets_sold
                FROM bookings
                WHERE status = 'confirmed' 
                  AND created_at >= %s AND created_at < %s
                GROUP BY period
                ORDER BY period ASC
            """, (granularity, start_date, end_date))
            
            rows = await cursor.fetchall()
            return [
                TimeSeriesPoint(
                    timestamp=row['period'],
                    revenue=float(row['revenue']),
                    tickets_sold=int(row['tickets_sold'])
                ) for row in rows
            ]

    # used for "get best performing events last year" type of queries
    async def get_sales_summaries_for_top_k_events(self, start_date: datetime, end_date: datetime, top_k: int) -> list[EventSalesSummary]:
        async with self.db_session.cursor() as cursor:
            await cursor.execute("""
                SELECT
                    e.id,
                    e.name,
                    e.event_date,
                    COALESCE(SUM(b.total_price) FILTER (WHERE b.status = 'confirmed'), 0) AS confirmed_revenue,
                    COALESCE(SUM(b.ticket_count) FILTER (WHERE b.status = 'confirmed'), 0) AS sold_tickets,
                    COUNT(b.id) FILTER (WHERE b.status = 'confirmed') AS confirmed_bookings_count,
                    CASE 
                        WHEN e.total_tickets IS NULL OR e.total_tickets = 0 THEN 0 
                        ELSE (COALESCE(SUM(b.ticket_count) FILTER (WHERE b.status = 'confirmed'), 0)::float / e.total_tickets)
                    END AS sell_through_rate
                FROM events e
                LEFT JOIN bookings b ON e.id = b.event_id
                WHERE e.created_at >= %s AND e.created_at < %s
                GROUP BY e.id, e.name, e.event_date, e.total_tickets
                ORDER BY confirmed_revenue DESC
                LIMIT %s
            """, (start_date, end_date, top_k))
            
            rows = await cursor.fetchall()
            return [
                EventSalesSummary(
                    event_id=Event.build_entity_id_from_uuid(row['id']),
                    event_name=row['name'],
                    event_date=row['event_date'],
                    confirmed_revenue=row['confirmed_revenue'],
                    sold_tickets=row['sold_tickets'],
                    confirmed_bookings_count=row['confirmed_bookings_count'],
                    sell_through_rate=row['sell_through_rate']
                ) for row in rows
            ]

    async def get_sales_summary_by_event_id(self, start_date: datetime, end_date: datetime, event_id: EntityId) -> EventSalesSummary | None:
        async with self.db_session.cursor() as cursor:
            await cursor.execute("""
                SELECT
                    e.id,
                    e.name,
                    e.event_date,
                    COALESCE(SUM(b.total_price) FILTER (WHERE b.status = 'confirmed'), 0) AS confirmed_revenue,
                    COALESCE(SUM(b.ticket_count) FILTER (WHERE b.status = 'confirmed'), 0) AS sold_tickets,
                    COUNT(b.id) FILTER (WHERE b.status = 'confirmed') AS confirmed_bookings_count,
                    CASE 
                        WHEN e.total_tickets IS NULL OR e.total_tickets = 0 THEN 0 
                        ELSE (COALESCE(SUM(b.ticket_count) FILTER (WHERE b.status = 'confirmed'), 0)::float / e.total_tickets)
                    END AS sell_through_rate
                FROM events e
                LEFT JOIN bookings b ON e.id = b.event_id
                WHERE e.id = %s AND e.created_at >= %s AND e.created_at < %s
                GROUP BY e.id, e.name, e.event_date, e.total_tickets
            """, (event_id.value, start_date, end_date))
            
            row = await cursor.fetchone()
            if not row:
                return None
            
            return EventSalesSummary(
                event_id=Event.build_entity_id_from_uuid(row['id']),
                event_name=row['name'],
                event_date=row['event_date'],
                confirmed_revenue=row['confirmed_revenue'],
                sold_tickets=row['sold_tickets'],
                confirmed_bookings_count=row['confirmed_bookings_count'],
                sell_through_rate=row['sell_through_rate']
            )

    async def get_tiers_sales_summaries_by_event_id(
        self, event_id: EntityId, start_date: datetime, end_date: datetime
    ) -> list[TierSalesSummary]:
        async with self.db_session.cursor() as cursor:
            await cursor.execute("""
                SELECT
                    et.id,
                    et.name AS tier_name,
                    e.id AS event_id,
                    COALESCE(COUNT(btt.id) FILTER (WHERE b.status = 'confirmed'), 0) AS sold_tickets,
                    COALESCE(SUM(btt.unit_price) FILTER (WHERE b.status = 'confirmed'), 0) AS revenue,
                    CASE
                        WHEN et.total_tickets = 0 THEN 0
                        ELSE (COALESCE(COUNT(btt.id) FILTER (WHERE b.status = 'confirmed'), 0)::float / et.total_tickets)
                    END AS sell_through_rate
                FROM event_tiers et
                JOIN events e ON et.event_id = e.id
                LEFT JOIN booking_tiered_tickets btt ON btt.ticket_tier_id = et.id
                LEFT JOIN bookings b ON b.id = btt.booking_id
                    AND b.created_at >= %s AND b.created_at < %s
                WHERE et.event_id = %s
                GROUP BY et.id, et.name, et.total_tickets, e.id
                ORDER BY revenue DESC
            """, (start_date, end_date, event_id.value))

            rows = await cursor.fetchall()
            return [
                TierSalesSummary(
                    tier_id=EventTier.build_entity_id_from_uuid(row['id']),
                    tier_name=row['tier_name'],
                    event_id=Event.build_entity_id_from_uuid(row['event_id']),
                    sold_tickets=row['sold_tickets'],
                    revenue=row['revenue'],
                    sell_through_rate=row['sell_through_rate']
                ) for row in rows
            ]