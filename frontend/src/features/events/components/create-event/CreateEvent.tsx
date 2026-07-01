import { useEffect } from "react";
import { useNavigate } from "@tanstack/react-router";
import { toast } from "sonner";
import {
  EventType,
  type CreateEventRequest,
  type EventSeatInput,
  type EventTierInput,
} from "../../types";
import { useCreateEventStore } from "../../stores/useCreateEventStore";
import { useCreateEvent } from "../../hooks/useCreateEvent";
import { EventTypeSwitch } from "./EventTypeSwitch";
import { SeatedEditor } from "./seated/SeatedEditor";
import { OpenFieldEditor } from "./open-field/OpenFieldEditor";
import { seatNumber } from "./utils";
import { Input, Textarea, Label, Button, Card, CardContent, CardHeader, CardTitle } from "@/components/ui";

const buildRequestPayload = (
  state: ReturnType<typeof useCreateEventStore.getState>,
): CreateEventRequest => {
  const base: Omit<CreateEventRequest, "seats" | "tiers"> = {
    name: state.name.trim(),
    description: state.description.trim(),
    venue: state.venue.trim(),
    event_date: state.eventDate,
    event_type: state.eventType,
    banner_url: state.bannerUrl.trim()
  };

  if (state.eventType === EventType.SEATED) {
    const tierById = new Map(state.seatedTiers.map((t) => [t.id, t]));
    const seats: EventSeatInput[] = [];
    for (let r = 0; r < state.rows; r++) {
      for (let c = 0; c < state.cols; c++) {
        const tierId = state.seatAssignments[r]?.[c] ?? null;
        const tier = tierId ? tierById.get(tierId) : undefined;
        seats.push({
          seat_number: seatNumber(r, c),
          price: tier?.price ?? 0,
        });
      }
    }
    return { ...base, seats, tiers: [] };
  }

  // OPEN_FIELD
  const tiers: EventTierInput[] = state.openFieldTiers.map((t) => ({
    name: t.name.trim(),
    price: t.price,
    total_tickets: t.totalTickets,
  }));
  return { ...base, seats: [], tiers };
};

const validate = (
  state: ReturnType<typeof useCreateEventStore.getState>,
): string | null => {
  const { name, description, venue, eventDate, bannerUrl } = state;
  if (!name.trim()) return "Event name is required.";
  if (!description.trim()) return "Description is required.";
  if (!venue.trim()) return "Venue is required.";
  if (!eventDate) return "Date and time is required.";
  if (!bannerUrl) return "Banner URL is required.";

  if (state.eventType === EventType.SEATED) {
    if (!state.gridConfirmed) return "Confirm the seat grid dimensions first.";
    if (state.seatedTiers.length < 1)
      return "Add at least one tier to price seats.";
    for (const tier of state.seatedTiers) {
      if (!tier.name.trim()) return "All tiers must have a name.";
      if (tier.price <= 0)
        return `Tier "${tier.name || "unnamed"}" must have a price greater than 0.`;
    }
    const unassigned = state.seatAssignments
      .flat()
      .filter((c) => c === null).length;
    if (unassigned > 0)
      return `${unassigned} seat(s) have no tier assigned. Assign a tier to all seats.`;
  } else {
    // OPEN_FIELD
    if (state.openFieldTiers.length < 1) return "Add at least one tier.";
    for (const tier of state.openFieldTiers) {
      if (!tier.name.trim()) return "All tiers must have a name.";
      if (tier.price <= 0)
        return `Tier "${tier.name || "unnamed"}" must have a price greater than 0.`;
      if (tier.totalTickets < 1)
        return `Tier "${tier.name || "unnamed"}" must have at least 1 ticket.`;
    }
  }

  return null;
};

export function CreateEvent() {
  const navigate = useNavigate();
  const { mutate, isPending } = useCreateEvent();
  const reset = useCreateEventStore((s) => s.reset);

  // common fields selectors
  const name = useCreateEventStore((s) => s.name);
  const description = useCreateEventStore((s) => s.description);
  const venue = useCreateEventStore((s) => s.venue);
  const eventDate = useCreateEventStore((s) => s.eventDate);
  const eventType = useCreateEventStore((s) => s.eventType);
  const bannerUrl = useCreateEventStore((s) => s.bannerUrl);
  const setName = useCreateEventStore((s) => s.setName);
  const setDescription = useCreateEventStore((s) => s.setDescription);
  const setVenue = useCreateEventStore((s) => s.setVenue);
  const setEventDate = useCreateEventStore((s) => s.setEventDate);
  const setBannerUrl = useCreateEventStore((s) => s.setBannerUrl);

  // reset store on unmount
  useEffect(() => {
    return () => reset();
  }, [reset]);

  const handleCreate = () => {
    const state = useCreateEventStore.getState();
    const error = validate(state);
    if (error) {
      toast.error(error);
      return;
    }

    const payload = buildRequestPayload(state);
    mutate(payload, {
      onSuccess: () => {
        toast.success("Event created");
        reset();
        navigate({ to: "/events" });
      },
      onError: () => {}, // already toasted by global MutationCache
    });
  };

  return (
    <div className="mx-auto max-w-4xl space-y-6 py-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Create Event</h1>
        <Button variant="ghost" onClick={() => navigate({ to: "/events" })}>
          Cancel
        </Button>
      </div>

      {/* Common fields */}
      <Card>
        <CardHeader>
          <CardTitle>Event Details</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-1.5">
            <Label htmlFor="name">Event Name</Label>
            <Input
              id="name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="e.g. Summer Jazz Night"
            />
          </div>
          <div className="space-y-1.5">
            <Label htmlFor="description">Description</Label>
            <Textarea
              id="description"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Describe the event..."
              rows={3}
            />
          </div>
          <div className="space-y-1.5">
            <Label htmlFor="venue">Venue</Label>
            <Input
              id="venue"
              value={venue}
              onChange={(e) => setVenue(e.target.value)}
              placeholder="e.g. The Grand Hall"
            />
          </div>
          <div className="space-y-1.5">
            <Label htmlFor="eventDate">Date &amp; Time</Label>
            <Input
              id="eventDate"
              type="datetime-local"
              value={eventDate}
              onChange={(e) => setEventDate(e.target.value)}
            />
          </div>
          <div className="space-y-1.5">
            <Label htmlFor="bannerUrl">Banner URL</Label>
            <Input
              id="bannerUrl"
              value={bannerUrl}
              onChange={(e) => setBannerUrl(e.target.value)}
              placeholder="e.g. https://..."
            />
          </div>
          <EventTypeSwitch />
        </CardContent>
      </Card>

      {/* Type-specific editor */}
      <Card>
        <CardHeader>
          <CardTitle>
            {eventType === EventType.SEATED
              ? "Seat Configuration"
              : "Ticket Tiers"}
          </CardTitle>
        </CardHeader>
        <CardContent>
          {eventType === EventType.SEATED ? (
            <SeatedEditor />
          ) : (
            <OpenFieldEditor />
          )}
        </CardContent>
      </Card>

      {/* Footer actions */}
      <div className="flex justify-end gap-3">
        <Button variant="outline" onClick={() => navigate({ to: "/events" })}>
          Cancel
        </Button>
        <Button onClick={handleCreate} disabled={isPending}>
          {isPending ? "Creating..." : "Create"}
        </Button>
      </div>
    </div>
  );
}
