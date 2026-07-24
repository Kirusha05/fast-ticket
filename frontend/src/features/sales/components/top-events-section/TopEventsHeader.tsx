import { DateRangePicker } from "../common/DateRangePicker";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

interface IProps {
  dateRange: {
    start: Date;
    end: Date;
  };
  setDateRange: (range: { start: Date; end: Date }) => void;
  setTopK: (k: number) => void;
}

export const TopEventsHeader = ({
  dateRange,
  setDateRange,
  setTopK,
}: IProps) => {
  const handleTopKChange = (value: string) => {
    const k = Number(value);

    if (Number.isInteger(k) && k >= 1) {
      setTopK(k);
    }
  };

  return (
    <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
      <div>
        <h2 className="text-2xl font-bold tracking-tight">
          Top Performing Events
        </h2>
        <p className="text-muted-foreground">
          Leaderboard of the highest-revenue events held during the selected period.
        </p>
      </div>

      <div className="flex flex-col gap-2 sm:flex-row sm:items-end">
        <div className="flex flex-col gap-1.5">
          <Label htmlFor="top-k" className="text-xs text-muted-foreground">
            Num. of events
          </Label>
          <Input
            id="top-k"
            type="number"
            min={1}
            defaultValue={5}
            onChange={(e) => handleTopKChange(e.target.value)}
            className="w-28"
          />
        </div>

        <DateRangePicker
          dateRange={dateRange}
          setDateRange={setDateRange}
        />
      </div>
    </div>
  );
};