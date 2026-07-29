import http from "k6/http";
import { check } from "k6";
import { Counter } from "k6/metrics";

// const successfulBookings = new Counter("successful_bookings");

export const options = {
  stages: [
    { duration: "5s", target: 200 }, // Ramp up over 5 seconds
    { duration: "30s", target: 200 }, // Stay at x users for 30 seconds (steady state)
    { duration: "5s", target: 0 }, // Ramp down to 0 users over 5 seconds
  ],
  thresholds: {
    // http_req_failed: ["rate<0.01"], // Error rate must be less than 1%
    http_req_duration: ["p(95)<50", "p(99)<500"], // 95% of requests must complete under 50ms
  },
};

const eventId = "e-22222222-2222-2222-2222-222222222222";
const tierId = "et-22222222-2222-2222-2222-222222222222";
const userAuth0Ids = [
  "auth0_1111",
  "auth0_2222",
  "auth0_3333",
  "auth0_4444",
  "auth0_5555",
];

export default function () {
  const randomUserAuth0Idx = Math.floor(Math.random() * userAuth0Ids.length);
  const userAuth0Id = userAuth0Ids[randomUserAuth0Idx];

  const res = http.post(
    "http://localhost:8000/bookings",
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

  check(res, {
    "booking accepted or sold out": (r) => r.status === 201 || r.status === 409,
  });
}
