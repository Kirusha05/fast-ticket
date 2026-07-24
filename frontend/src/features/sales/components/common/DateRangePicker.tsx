import { useState } from "react";
import type { DateRange } from "react-day-picker";

import { CalendarIcon } from "lucide-react";
import { cn } from "@/lib/utils";

import {
  Button,
  Calendar,
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui";

import {
  format,
  subDays,
  subMonths,
  subYears,
  startOfDay,
  endOfDay,
  isToday,
  startOfYear,
} from "date-fns";

// Normalize a range so "start" is always 00:00:00 local time, and "end" is
// the end of that day (23:59:59.999), unless "end" falls on today, in which
// case we keep the current time
const normalizeRange = (start: Date, end: Date): { start: Date; end: Date } => {
  const normalizedStart = startOfDay(start);
  const normalizedEnd = isToday(end) ? new Date() : endOfDay(end);

  return { start: normalizedStart, end: normalizedEnd };
};

interface IProps {
  dateRange: {
    start: Date;
    end: Date;
  };
  setDateRange: (range: { start: Date; end: Date }) => void;
}

export const DateRangePicker = ({ dateRange, setDateRange }: IProps) => {
  const [open, setOpen] = useState(false);

  const selectedRange: DateRange = {
    from: dateRange.start,
    to: dateRange.end,
  };

  // Each preset's "end" is "today", so it's left as the current moment,
  // while "start" is normalized to the start of its day.
  const presets = [
    {
      label: "Today",
      getRange: () => {
        const today = new Date();
        return normalizeRange(today, today);
      },
    },
    {
      label: "Last 7 days",
      getRange: () => {
        const today = new Date();
        return normalizeRange(subDays(today, 6), today);
      },
    },
    {
      label: "Last 14 days",
      getRange: () => {
        const today = new Date();
        return normalizeRange(subDays(today, 13), today);
      },
    },
    {
      label: "Last month",
      getRange: () => {
        const today = new Date();
        return normalizeRange(subMonths(today, 1), today);
      },
    },
    {
      label: "Last 3 months",
      getRange: () => {
        const today = new Date();
        return normalizeRange(subMonths(today, 3), today);
      },
    },
    {
      label: "Last 6 months",
      getRange: () => {
        const today = new Date();
        return normalizeRange(subMonths(today, 6), today);
      },
    },
    {
      label: "Last year",
      getRange: () => {
        const today = new Date();
        return normalizeRange(subYears(today, 1), today);
      },
    },
    {
      label: "Year To Date",
      getRange: () => {
        const today = new Date();
        return normalizeRange(startOfYear(today), today);
      },
    },
  ];

  return (
    <Popover open={open} onOpenChange={setOpen}>
      <PopoverTrigger asChild>
        <Button
          variant="outline"
          className={cn(
            "w-[280px] justify-start bg-background text-left font-normal",
          )}
        >
          <CalendarIcon className="mr-1 h-4 w-4 opacity-70" />

          {selectedRange.from && selectedRange.to ? (
            <>
              {format(selectedRange.from, "MMM d, yyyy")} –{" "}
              {format(selectedRange.to, "MMM d, yyyy")}
            </>
          ) : (
            "Select date range"
          )}
        </Button>
      </PopoverTrigger>

      <PopoverContent className="w-auto p-0" align="end">
        <Calendar
          mode="range"
          numberOfMonths={2}
          defaultMonth={selectedRange.from}
          selected={selectedRange}
        //   disabled={(date) => date > new Date()}
          onSelect={(range) => {
            if (!range?.from) return;

            const { start, end } = normalizeRange(
              range.from,
              range.to ?? range.from,
            );
            setDateRange({ start, end });

            if (range.to) {
              setOpen(false);
            }
          }}
        />

        <div className="border-t p-3 grid grid-cols-2 gap-2">
          {presets.map((preset) => (
            <Button
              key={preset.label}
              variant="outline"
              size="sm"
              onClick={() => {
                setDateRange(preset.getRange());
                setOpen(false);
              }}
            >
              {preset.label}
            </Button>
          ))}
        </div>
      </PopoverContent>
    </Popover>
  );
};
