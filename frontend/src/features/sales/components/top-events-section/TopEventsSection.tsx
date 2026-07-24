import { useState } from "react";
import { subMonths } from "date-fns";
import { TopEventsHeader } from "./TopEventsHeader";
import { TopEventsLeaderboard } from "./TopEventsLeaderboard";


export const TopEventsSection = () => {
  // Default to last month
  const [dateRange, setDateRange] = useState<{ start: Date; end: Date }>({
    start: subMonths(new Date(), 1),
    end: new Date(),
  });
  const [topK, setTopK] = useState(5);

  return (
    <section className="space-y-6 border-t pt-6">
      <TopEventsHeader dateRange={dateRange} setDateRange={setDateRange} setTopK={setTopK} />
      <TopEventsLeaderboard dateRange={dateRange} topK={topK} />
    </section>
  );
};