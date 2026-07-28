import React, { useState } from "react";
import { subMonths } from "date-fns";
import { EventDetailToolbar } from "./EventDetailToolbar";
import { EventSummaryCards } from "./EventSummaryCards";
import { EventType, type Event } from "@/features/events/types";
import { EventTiersBreakdown } from "./EventTiersBreakdown";
import { Layers } from "lucide-react";

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

      {!selectedEvent && (
        <div className="flex flex-col items-center justify-center py-12 text-center">
          <div className="mb-4 rounded-full bg-muted p-3">
            <Layers className="h-8 w-8 text-muted-foreground" />
          </div>

          <p className="font-medium">No events selected</p>

          <p className="mt-1 text-sm text-muted-foreground">
            Select an event to view its sales performance.
          </p>
        </div>
      )}
    </section>
  );
};
