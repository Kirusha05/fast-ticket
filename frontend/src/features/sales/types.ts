export type SalesGranularity = "day" | "week" | "month";

export interface SalesSummary {
  confirmed_revenue: number;
  lost_revenue: number;
  confirmed_bookings_count: number;
  sold_tickets: number;
}

export interface TimeSeriesPoint {
  timestamp: string;
  revenue: number;
  tickets_sold: number;
}

export interface EventSalesSummary {
  event_id: string;
  event_name: string;
  event_date: string;
  confirmed_revenue: number;
  sold_tickets: number;
  confirmed_bookings_count: number;
  sell_through_rate: number;
}

export interface TierSalesSummary {
  tier_id: string;
  tier_name: string;
  event_id: string;
  sold_tickets: number;
  revenue: number;
  sell_through_rate: number;
}
