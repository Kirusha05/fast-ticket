import { useState } from "react";
import { cn } from "@/lib/utils";
import {
  Button,
  Command,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
  Popover,
  PopoverContent,
  PopoverTrigger,
  Skeleton,
} from "@/components/ui";
import { DateRangePicker } from "../common/DateRangePicker";
import { useGetEvents } from "@/features/events/hooks/useGetEvents";
import { Check, ChevronsUpDown, Ticket, Search } from "lucide-react";
import { type Event } from "@/features/events/types";
import { format } from "date-fns";

interface IProps {
  selectedEvent: Event | null;
  setSelectedEvent: (event: Event | null) => void;
  dateRange: { start: Date; end: Date };
  setDateRange: (range: { start: Date; end: Date }) => void;
}

export const EventDetailToolbar = ({
  selectedEvent,
  setSelectedEvent,
  dateRange,
  setDateRange,
}: IProps) => {
  const [isEventOpen, setIsEventOpen] = useState(false);
  const { data: events, isLoading } = useGetEvents();

  return (
    <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
      <div>
        <h2 className="text-2xl font-bold tracking-tight">Event Details</h2>
        <p className="text-muted-foreground">
          Select an event to view its performance during the selected period.
        </p>
      </div>

      <div className="flex flex-col gap-2 sm:flex-row sm:items-center">
        {/* Event Selector (Combobox) */}
        <Popover open={isEventOpen} onOpenChange={setIsEventOpen}>
          <PopoverTrigger asChild>
            <Button
              variant="outline"
              role="combobox"
              aria-expanded={isEventOpen}
              className="w-full sm:w-[300px] justify-between font-normal bg-card"
            >
              {selectedEvent ? (
                <span className="flex items-center gap-2 truncate">
                  <Ticket className="h-4 w-4 text-muted-foreground" />
                  {selectedEvent.name} ({format(new Date(selectedEvent.event_date), "MMM dd, yyyy")})
                </span>
              ) : (
                <span className="flex items-center gap-2 text-muted-foreground">
                  <Search className="h-4 w-4" />
                  Search event...
                </span>
              )}
              <ChevronsUpDown className="ml-2 h-4 w-4 shrink-0 opacity-50" />
            </Button>
          </PopoverTrigger>
          <PopoverContent className="w-[300px] p-0" align="start">
            <Command>
              <CommandInput placeholder="Search event..." />
              <CommandList>
                <CommandEmpty>No event found.</CommandEmpty>
                <CommandGroup>
                  {isLoading ? (
                    <div className="p-2 space-y-2">
                      <Skeleton className="h-8 w-full" />
                      <Skeleton className="h-8 w-full" />
                    </div>
                  ) : (
                    events?.map((event) => (
                      <CommandItem
                        key={event.id}
                        value={event.name}
                        onSelect={() => {
                          setSelectedEvent(
                            event.id === selectedEvent?.id ? null : event,
                          );
                          setIsEventOpen(false);
                        }}
                      >
                        <Check
                          className={cn(
                            "mr-2 h-4 w-4",
                            selectedEvent?.id === event.id
                              ? "opacity-100"
                              : "opacity-0",
                          )}
                        />
                        <div>
                          <p className="truncate font-medium">{event.name}</p>
                          <p className="text-xs text-muted-foreground">
                            {format(new Date(event.event_date), "MMM dd, yyyy")}
                          </p>
                        </div>
                      </CommandItem>
                    ))
                  )}
                </CommandGroup>
              </CommandList>
            </Command>
          </PopoverContent>
        </Popover>

        {/* Date Range Picker */}
        <DateRangePicker dateRange={dateRange} setDateRange={setDateRange} />
      </div>
    </div>
  );
};
