import { Badge, Button, Card, CardContent, Separator } from "@/components/ui";
import { Link } from "@tanstack/react-router";
import { CalendarDays, ExternalLink, MapPin } from "lucide-react";
import { usd } from "@/features/bookings/components/new-booking/utils";
import { useIsMobile } from "@/hooks/use-mobile";
import { type Event } from "@/features/events/types";
import { type Ticket, TicketStatus } from "../../types";
import { QRCodeSVG } from "qrcode.react";

const dateFormat = new Intl.DateTimeFormat("en-US", {
  dateStyle: "medium",
  timeStyle: "short",
});

interface IProps {
  event: Event;
  ticket: Ticket;
}

export const TicketCard = ({ event, ticket }: IProps) => {
  const isMobile = useIsMobile();

  const formattedEventDate = dateFormat.format(new Date(event.event_date));

  return (
    <Card className="flex-col md:flex-row gap-0 md:gap-2 overflow-hidden py-0 transition-shadow hover:shadow-md">
      {/* event banner — clickable to event page */}
      <Link
        to="/events/$eventId"
        params={{ eventId: event.id }}
        className="shrink-0"
      >
        <img
          src={event.banner_url}
          alt={event.name}
          className="aspect-[4/3] w-full md:w-auto h-60 shrink-0 cursor-pointer object-cover transition-opacity hover:opacity-80"
        />
      </Link>

      <CardContent className="flex min-w-0 flex-1 flex-col justify-start p-4">
        <div className="space-y-2">
          {/* row 1: event name + status */}
          <div className="flex items-center justify-between gap-2">
            <span className="truncate text-sm font-semibold">{event.name}</span>
            <div className="flex items-center gap-1.5 shrink-0">
              <Button variant="outline" size="sm" asChild>
                <Link to="/events/$eventId" params={{ eventId: event.id }}>
                  <ExternalLink className="h-3.5 w-3.5" />
                  View event
                </Link>
              </Button>
            </div>
          </div>

          {/* row 2: venue + date */}
          <div className="flex flex-wrap items-center gap-x-4 gap-y-2 text-xs text-muted-foreground mt-4 md:mt-0">
            <span className="inline-flex items-center gap-1">
              <MapPin className="h-3.5 w-3.5 shrink-0" />
              {event.venue}
            </span>
            <span className="inline-flex items-center gap-1">
              <CalendarDays className="h-3.5 w-3.5 shrink-0" />
              {formattedEventDate}
            </span>
          </div>

          <Separator className="my-4" />
        </div>

        {/* row 4: count + total */}
        <div className="flex flex-col items-start gap-2 justify-between text-xs md:text-sm flex-1">
          {ticket.tier_name && (
            <p className="text-muted-foreground">
              Tier:{" "}
              <span className="font-bold text-white">{ticket.tier_name}</span>
            </p>
          )}
          {ticket.seat_number && (
            <p className="text-muted-foreground">
              Seat:{" "}
              <span className="font-bold text-white">{ticket.seat_number}</span>
            </p>
          )}
          <div className="w-full flex items-center justify-between gap-1.5 shrink-0">
            <p className="inline-flex items-center gap-1 text-muted-foreground">
              <span className="mr-1">Purchased:</span>
              <CalendarDays className="h-3.5 w-3.5 shrink-0" />
              {dateFormat.format(new Date(ticket.created_at))}
            </p>
            <span className="font-semibold">
              {usd.format((ticket.tier_price || ticket.seat_price)!)}
            </span>
          </div>
        </div>

        <Separator orientation="horizontal" className="my-4" />

        <div className="flex items-center gap-1">
          <Badge
            className={`capitalize mr-1 ${ticket.status == TicketStatus.USED ? "bg-green-500" : ""}`}
            variant={
              ticket.status == TicketStatus.USED ? "default" : "secondary"
            }
          >
            {ticket.status == TicketStatus.UNUSED ? ticket.status : "validated"}
          </Badge>
          {ticket.status == TicketStatus.USED && (
            <>
              <p className="inline-flex items-center gap-1 text-muted-foreground">
                <span>on</span>
                <CalendarDays className="h-3.5 w-3.5 shrink-0" />
                {dateFormat.format(new Date(ticket.checked_in_at!))}
              </p>
            </>
          )}
        </div>
      </CardContent>

      <Separator orientation="vertical" />

      <div key={ticket.id} className="flex flex-col items-center gap-3 p-4">
        <div className="bg-white border border-black rounded-xl p-4">
          <QRCodeSVG
            value={ticket.id}
            size={isMobile ? 256 : 140}
            level="M"
            bgColor="#FFFFFF"
            fgColor="#000000"
          />
        </div>
        <p className="text-white text-xs text-center tracking-wide">
          {ticket.id}
        </p>
      </div>
    </Card>
  );
};
