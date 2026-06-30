import { EventType } from "../../types";
import { useCreateEventStore } from "../../stores/useCreateEventStore";

export function EventTypeSwitch() {
  const eventType = useCreateEventStore((s) => s.eventType);
  const setEventType = useCreateEventStore((s) => s.setEventType);

  return (
    <div className="flex items-center gap-2">
      <span className="text-sm font-medium">Event type:</span>
      <div className="flex overflow-hidden rounded-md border border-border">
        <button
          type="button"
          onClick={() => setEventType(EventType.SEATED)}
          className={`px-4 py-1.5 text-sm font-medium transition-colors ${
            eventType === EventType.SEATED
              ? "bg-primary text-primary-foreground"
              : "bg-background text-muted-foreground hover:bg-muted"
          }`}
        >
          Seated
        </button>
        <button
          type="button"
          onClick={() => setEventType(EventType.OPEN_FIELD)}
          className={`px-4 py-1.5 text-sm font-medium transition-colors ${
            eventType === EventType.OPEN_FIELD
              ? "bg-primary text-primary-foreground"
              : "bg-background text-muted-foreground hover:bg-muted"
          }`}
        >
          Open Field
        </button>
      </div>
    </div>
  );
}