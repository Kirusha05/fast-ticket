import { useState } from "react";
import { subDays } from "date-fns";
import type { SalesGranularity } from "../../types";
import { OverallToolbar } from "./OverallToolbar";
import { OverallKpiCards } from "./KpiCards";
import { SalesOverTimeChart } from "./SalesOverTimeChart";

export const OverallAnalyticsSection = () => {
  // Default to last 30 days
  const [dateRange, setDateRange] = useState<{ start: Date; end: Date }>({
    start: subDays(new Date(), 30),
    end: new Date(),
  });
  const [granularity, setGranularity] = useState<SalesGranularity>("day");

  return (
    <section className="space-y-6">
      <OverallToolbar
        dateRange={dateRange}
        setDateRange={setDateRange}
        granularity={granularity}
        setGranularity={setGranularity}
      />
      <OverallKpiCards dateRange={dateRange} />
      <SalesOverTimeChart dateRange={dateRange} granularity={granularity} />
    </section>
  );
};