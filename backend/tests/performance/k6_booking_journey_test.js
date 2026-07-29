import http from "k6/http";
import { check, sleep } from "k6";
import { Counter } from "k6/metrics";

const successfulBookings = new Counter("successful_bookings");

export const options = {
  stages: [
    { duration: "15s", target: 1000 }, // Ramp up over 15 seconds
    { duration: "30s", target: 1000 }, // Stay at x users for 30 seconds (steady state)
    { duration: "15s", target: 0 }, // Ramp down to 0 users over 15 seconds
  ],
  thresholds: {
    // http_req_failed: ["rate<0.01"], // Error rate must be less than 1%
    http_req_duration: ["p(95)<50", "p(99)<500"], // 95% of requests must complete under 50ms
    successful_bookings: ["count==10000"],  // 10000 successful bookings for event's 20000 total tickets
  },
};

const userAuth0Ids = [
  "auth0_1111",
  "auth0_2222",
  "auth0_3333",
  "auth0_4444",
  "auth0_5555",
];

export default function () {
  const eventsRes = http.get(
    "http://localhost:8000/events?event_type=open_field",
  );

  const events = JSON.parse(eventsRes.body);
  const randomEventIdx = Math.floor(Math.random() * events.length);
  const eventId = events[randomEventIdx].id;

  sleep(1);

  const eventRes = http.get(`http://localhost:8000/events/${eventId}`);

  const event = JSON.parse(eventRes.body);
  const tierId = event.tiers[0].id;

  sleep(1);

  const randomUserAuth0Idx = Math.floor(Math.random() * userAuth0Ids.length);
  const userAuth0Id = userAuth0Ids[randomUserAuth0Idx];

  const bookingRes = http.post(
    `http://localhost:8000/bookings`,
    JSON.stringify({
      event_id: eventId,
      tiered_tickets: [
        {
          tier_id: tierId,
          count: 2,
        },
      ],
    }),
    {
      headers: {
        "Content-Type": "application/json",
        "X-Load-Test-User": userAuth0Id,
      },
    },
  );

  check(bookingRes, {
    "booking accepted or sold out": (r) => r.status === 201 || r.status === 409,
  });

  if (bookingRes.status === 201) {
    successfulBookings.add(1);
  }

  sleep(1);
}
