import { EventDetailSection } from "./event-detail-section/EventDetailSection";
import { OverallAnalyticsSection } from "./overall-analytics-section/OverallAnalyticsSection";
import { TopEventsSection } from "./top-events-section/TopEventsSection";

export function SalesPage() {
  return (
    <div className="space-y-10 container mx-auto">
      {/* Header */}
      {/* <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Sales</h1>
      </div> */}

      <OverallAnalyticsSection />
      <TopEventsSection />
      <EventDetailSection />
    </div>
  );
}
