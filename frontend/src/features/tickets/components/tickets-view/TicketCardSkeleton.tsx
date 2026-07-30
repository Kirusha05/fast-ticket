import { Card, CardContent, Separator, Skeleton } from "@/components/ui";

export const TicketCardSkeleton = () => {
  return (
    <Card className="flex-col md:flex-row gap-0 md:gap-2 overflow-hidden py-0">
      {/* event banner */}
      <Skeleton className="aspect-[4/3] w-full md:w-60 h-60 shrink-0 rounded-none" />

      <CardContent className="flex min-w-0 flex-1 flex-col justify-start p-4">
        <div className="space-y-2">
          {/* row 1: event name + button */}
          <div className="flex items-center justify-between gap-2">
            <Skeleton className="h-4 w-40" />
            <Skeleton className="h-8 w-28 shrink-0" />
          </div>

          {/* row 2: venue + date */}
          <div className="flex flex-wrap items-center gap-x-4 gap-y-2 mt-4 md:mt-0">
            <Skeleton className="h-3 w-24" />
            <Skeleton className="h-3 w-32" />
          </div>

          <Separator className="my-4" />
        </div>

        {/* row 3: tier / seat / purchased + total */}
        <div className="flex flex-col items-start gap-2 justify-between flex-1">
          <Skeleton className="h-3 w-28" />
          <Skeleton className="h-3 w-24" />
          <div className="w-full flex items-center justify-between gap-1.5 shrink-0">
            <Skeleton className="h-3 w-36" />
            <Skeleton className="h-4 w-16" />
          </div>
        </div>

        <Separator orientation="horizontal" className="my-4" />

        {/* row 4: status badge */}
        <div className="flex items-center gap-2">
          <Skeleton className="h-5 w-16 rounded-full" />
        </div>
      </CardContent>

      <Separator orientation="vertical" />

      {/* QR code block */}
      <div className="flex flex-col items-center gap-3 p-4">
        <Skeleton className="h-[172px] w-[172px] md:h-[172px] md:w-[172px] rounded-xl" />
        <Skeleton className="h-3 w-24" />
      </div>
    </Card>
  );
};