import React, { useState } from "react";
import { subMonths } from "date-fns";
import { EventDetailToolbar } from "./EventDetailToolbar";
import { EventSummaryCards } from "./EventSummaryCards";
import { EventType, type Event } from "@/features/events/types";
import { EventTiersBreakdown } from "./EventTiersBreakdown";

export const EventDetailSection: React.FC = () => {
  // Default to last month
  const [dateRange, setDateRange] = useState<{ start: Date; end: Date }>({
    start: subMonths(new Date(), 1),
    end: new Date(),
  });
  const [selectedEvent, setSelectedEvent] = useState<Event | null>(null);

  return (
    <section className="space-y-6 border-t pt-10">
      <EventDetailToolbar
        selectedEvent={selectedEvent}
        setSelectedEvent={setSelectedEvent}
        dateRange={dateRange}
        setDateRange={setDateRange}
      />
      {selectedEvent && (
        <EventSummaryCards
          selectedEvent={selectedEvent}
          dateRange={dateRange}
        />
      )}

      {selectedEvent && selectedEvent.event_type == EventType.OPEN_FIELD && (
        <EventTiersBreakdown
          selectedEvent={selectedEvent}
          dateRange={dateRange}
        />
      )}
    </section>
  );
};
