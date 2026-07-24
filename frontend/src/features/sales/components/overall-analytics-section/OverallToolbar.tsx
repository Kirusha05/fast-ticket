import type { SalesGranularity } from "../../types";
import { ToggleGroup, ToggleGroupItem } from "@/components/ui";
import { DateRangePicker } from "../common/DateRangePicker";

interface IProps {
  dateRange: {
    start: Date;
    end: Date;
  };
  setDateRange: (range: { start: Date; end: Date }) => void;
  granularity: SalesGranularity;
  setGranularity: (g: SalesGranularity) => void;
}

export const OverallToolbar = ({
  dateRange,
  setDateRange,
  granularity,
  setGranularity,
}: IProps) => {
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
        <DateRangePicker dateRange={dateRange} setDateRange={setDateRange} />

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
