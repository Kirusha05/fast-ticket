import { CalendarDays, MapPin } from "lucide-react";
import { useNavigate } from "@tanstack/react-router";
import type { Event } from "@/features/events/types";
import { Badge } from "@/components/ui/badge";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

interface IProps {
  event: Event;
};

export function EventCard({ event }: IProps) {
  const navigate = useNavigate();

  const formattedDate = new Intl.DateTimeFormat("en-US", {
    weekday: "short",
    month: "short",
    day: "numeric",
    year: "numeric",
  }).format(new Date(event.event_date));

  const eventTypeLabel = event.event_type === "seated" ? "Seated" : "Tiered";

  return (
    <Card
      className="cursor-pointer overflow-hidden transition-shadow hover:shadow-md"
      onClick={() => navigate({ to: `/events/${event.id}` })}
    >
      {/* Banner image, direct img child as ShadCN Card has [>img:first-child]:pt-0 defined */}
      <img
        src={event.banner_url}
        alt={event.name}
        className="aspect-[16/9] w-full object-cover transition-transform duration-300 group-hover/card:scale-105"
      />

      <CardHeader>
        <div className="flex items-start justify-between gap-2">
          <CardTitle className="text-lg font-semibold">{event.name}</CardTitle>
          <Badge variant="secondary" className="shrink-0">
            {eventTypeLabel}
          </Badge>
        </div>
      </CardHeader>

      <CardContent className="space-y-2">
        {/* Event date */}
        <div className="flex items-center gap-2 text-sm text-muted-foreground">
          <CalendarDays className="h-4 w-4 shrink-0" />
          <span>{formattedDate}</span>
        </div>

        {/* Venue */}
        <div className="flex items-center gap-2 text-sm text-muted-foreground">
          <MapPin className="h-4 w-4 shrink-0" />
          <span>{event.venue}</span>
        </div>
      </CardContent>
    </Card>
  );
}