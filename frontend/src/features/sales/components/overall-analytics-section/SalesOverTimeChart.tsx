import type { SalesGranularity } from "../../types";
import { useGetSalesOverTime } from "@/features/sales/hooks/useGetSalesOverTime";
import { format } from "date-fns";
import {
  ChartContainer,
  ChartLegend,
  ChartLegendContent,
  ChartTooltip,
  ChartTooltipContent,
  type ChartConfig,
  Skeleton,
} from "@/components/ui";

import { Area, AreaChart, CartesianGrid, XAxis, YAxis } from "recharts";

interface IProps {
  dateRange: { start: Date; end: Date };
  granularity: SalesGranularity;
}

const chartConfig = {
  revenue: {
    label: <span className="mr-8">Revenue</span>,
    color: "#10b981",
  },
  tickets_sold: {
    label: <span className="mr-8">Tickets Sold</span>,
    color: "#3b82f6",
  },
} satisfies ChartConfig;

export const SalesOverTimeChart = ({ dateRange, granularity }: IProps) => {
    const { data, isLoading } = useGetSalesOverTime(
      dateRange.start,
      dateRange.end,
      granularity,
    );

    const formattedData =
      data?.map((point) => ({
        ...point,
        date: format(new Date(point.timestamp), "MMM dd"),
  })) ?? [];

// Mock data
//   const isLoading = false;
//   granularity = "day";
//   const formattedData: {
//     date: string;
//     timestamp: string;
//     revenue: number;
//     tickets_sold: number;
//   }[] = [
//     {
//       timestamp: "2026-07-12T00:00:00Z",
//       revenue: 400,
//       tickets_sold: 14,
//       date: "Jul 12",
//     },
//     {
//       timestamp: "2026-07-17T00:00:00Z",
//       revenue: 650,
//       tickets_sold: 18,
//       date: "Jul 17",
//     },
//     {
//       timestamp: "2026-07-21T00:00:00Z",
//       revenue: 250,
//       tickets_sold: 10,
//       date: "Jul 21",
//     },
//     {
//       timestamp: "2026-07-23T00:00:00Z",
//       revenue: 300,
//       tickets_sold: 10,
//       date: "Jul 23",
//     },
//     {
//       timestamp: "2026-07-25T00:00:00Z",
//       revenue: 890,
//       tickets_sold: 24,
//       date: "Jul 25",
//     },
//   ];

  return (
    <div className="rounded-xl bg-black p-4">
      {isLoading ? (
        <Skeleton className="h-[500px] w-full bg-neutral-900" />
      ) : (
        <ChartContainer config={chartConfig} className="h-[500px] w-full">
          <AreaChart
            accessibilityLayer
            data={formattedData}
            margin={{
              top: 10,
              right: 10,
              left: 10,
              bottom: 0,
            }}
          >
            <defs>
              <linearGradient id="fillRevenue" x1="0" y1="0" x2="0" y2="1">
                <stop
                  offset="5%"
                  stopColor="var(--color-revenue)"
                  stopOpacity={0.35}
                />
                <stop
                  offset="95%"
                  stopColor="var(--color-revenue)"
                  stopOpacity={0}
                />
              </linearGradient>

              <linearGradient id="fillTickets" x1="0" y1="0" x2="0" y2="1">
                <stop
                  offset="5%"
                  stopColor="var(--color-tickets_sold)"
                  stopOpacity={0.35}
                />
                <stop
                  offset="95%"
                  stopColor="var(--color-tickets_sold)"
                  stopOpacity={0}
                />
              </linearGradient>
            </defs>

            <CartesianGrid vertical={false} stroke="rgba(255,255,255,0.08)" />

            <ChartTooltip cursor={false} content={<ChartTooltipContent />} />
            <ChartLegend content={<ChartLegendContent />} />

            <XAxis dataKey="date" hide />
            <YAxis yAxisId="revenue" hide domain={[0, "dataMax"]} />
            <YAxis yAxisId="tickets" hide domain={[0, "dataMax"]} />

            <Area
              yAxisId="revenue"
              type="monotone"
              dataKey="revenue"
              fill="url(#fillRevenue)"
              stroke="var(--color-revenue)"
              strokeWidth={2}
            />
            <Area
              yAxisId="tickets"
              type="monotone"
              dataKey="tickets_sold"
              fill="url(#fillTickets)"
              stroke="var(--color-tickets_sold)"
              strokeWidth={2}
            />
          </AreaChart>
        </ChartContainer>
      )}
    </div>
  );
};
