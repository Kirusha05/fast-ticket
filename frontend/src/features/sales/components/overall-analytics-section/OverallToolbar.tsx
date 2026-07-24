import { useState } from "react";
import { CalendarIcon } from "lucide-react";
import type { DateRange } from "react-day-picker";

import type { SalesGranularity } from "../../types";
import {
  Button,
  Calendar,
  Popover,
  PopoverContent,
  PopoverTrigger,
  ToggleGroup,
  ToggleGroupItem,
} from "@/components/ui";
import { cn } from "@/lib/utils";

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

interface IProps {
  dateRange: {
    start: Date;
    end: Date;
  };
  setDateRange: (range: { start: Date; end: Date }) => void;
  granularity: SalesGranularity;
  setGranularity: (g: SalesGranularity) => void;
}

// Normalize a range so "start" is always 00:00:00 local time, and "end" is
// the end of that day (23:59:59.999), unless "end" falls on today, in which
// case we keep the current time
const normalizeRange = (start: Date, end: Date): { start: Date; end: Date } => {
  const normalizedStart = startOfDay(start);
  const normalizedEnd = isToday(end) ? new Date() : endOfDay(end);

  return { start: normalizedStart, end: normalizedEnd };
};

export const OverallToolbar = ({
  dateRange,
  setDateRange,
  granularity,
  setGranularity,
}: IProps) => {
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
    <div className="flex flex-col gap-5 border-b pb-6 md:flex-row md:items-end md:justify-between">
      <div className="space-y-1">
        <h2 className="text-2xl font-semibold tracking-tight">
          Overall Analytics
        </h2>
        <p className="text-sm text-muted-foreground">
          Overview of your total sales performance.
        </p>
      </div>

      <div className="flex flex-wrap items-center gap-4">
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
              disabled={(date) => date > new Date()}
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
        
        <p className="text-sm text-muted-foreground">Chart granularity</p>
      
        <ToggleGroup
          type="single"
          variant="outline"
          value={granularity}
          onValueChange={(value) => {
            if (value) {
              setGranularity(value as SalesGranularity);
            }
          }}
        >
          <ToggleGroupItem value="day">Day</ToggleGroupItem>
          <ToggleGroupItem value="week">Week</ToggleGroupItem>
          <ToggleGroupItem value="month">Month</ToggleGroupItem>
        </ToggleGroup>
      </div>
    </div>
  );
};