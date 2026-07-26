INSERT INTO users (
    id,
    name,
    email,
    auth0_id,
    role
)
VALUES
(
    '11111111-1111-1111-1111-111111111111',
    'Test User',
    'test@test.com',
    'ababababababab',
    'user'
),
(
    '22222222-2222-2222-2222-222222222222',
    'Second User',
    'second@test.com',
    'cdcdcdcdcdcdcd',
    'user'
);


INSERT INTO events (
    id,
    name,
    description,
    venue,
    event_date,
    event_type,
    banner_url,
    total_tickets,
    available_tickets
)
VALUES (
    '11111111-1111-1111-1111-111111111111',
    'Summerfest',
    'Cel mai tare festival al verii',
    'Gradina Botanica',
    '2026-06-21',
    'open_field',
    'https://t4.ftcdn.net/jpg/06/00/62/77/360_F_600627754_uKAUfEHyXUdPHlZWldI47Z5TqZpGKhB7.jpg',
    10000,
    10000
),
(
    '22222222-2222-2222-2222-222222222222',
    'Opera Night',
    'O seara de opera clasica',
    'Ateneul Roman',
    '2026-06-21',
    'seated',
    'https://t4.ftcdn.net/jpg/06/00/62/77/360_F_600627754_uKAUfEHyXUdPHlZWldI47Z5TqZpGKhB7.jpg',
    1000,
    1000
),
(
    '33333333-3333-3333-3333-333333333333',
    'Rock Arena',
    'Concert rock cu trupe internationale',
    'Sala Palatului',
    '2026-07-15',
    'seated',
    'https://t4.ftcdn.net/jpg/06/00/62/77/360_F_600627754_uKAUfEHyXUdPHlZWldI47Z5TqZpGKhB7.jpg',
    500,
    500
);

INSERT INTO event_tiers (
    id,
    event_id,
    name,
    price,
    total_tickets,
    available_tickets
)
VALUES
(
    '77777777-7777-7777-7777-777777777777',
    '11111111-1111-1111-1111-111111111111',
    'General',
    50.00,
    10000,
    10000
);

INSERT INTO event_seats (
    id,
    event_id,
    seat_number,
    price,
    is_available
)
VALUES
(
    'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa',
    '22222222-2222-2222-2222-222222222222',
    'A1',
    150.00,
    TRUE
),
(
    'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb',
    '22222222-2222-2222-2222-222222222222',
    'A2',
    150.00,
    TRUE
),
(
    'cccccccc-cccc-cccc-cccc-cccccccccccc',
    '22222222-2222-2222-2222-222222222222',
    'B1',
    120.00,
    TRUE
),
(
    'dddddddd-dddd-dddd-dddd-dddddddddddd',
    '33333333-3333-3333-3333-333333333333',
    'A1',
    200.00,
    TRUE
),
(
    'eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeee',
    '33333333-3333-3333-3333-333333333333',
    'A2',
    200.00,
    TRUE
),
(
    'ffffffff-ffff-ffff-ffff-ffffffffffff',
    '33333333-3333-3333-3333-333333333333',
    'A3',
    200.00,
    TRUE
);

-- MAIN SECTION
INSERT INTO bookings (
    id,
    user_id,
    event_id,
    status,
    ticket_count,
    total_price,
    currency,
    expires_at
)
VALUES
-- user 1, open field event, 2 General tickets @ $50 each = $100
(
    '10000000-0000-0000-0000-000000000001',
    '11111111-1111-1111-1111-111111111111',
    '11111111-1111-1111-1111-111111111111',
    'pending',
    2,
    100.00,
    'usd',
    NOW() + INTERVAL '30 minutes'   -- expires 30 min from insert time
),
-- user 1, seated event, seats A1 + A2 @ $150 each = $300
(
    '10000000-0000-0000-0000-000000000002',
    '11111111-1111-1111-1111-111111111111',
    '22222222-2222-2222-2222-222222222222',
    'pending',
    2,
    300.00,
    'usd',
    NOW() + INTERVAL '30 minutes'   -- expires 30 min from insert time
),
-- user 2, open field event, 1 General ticket @ $50 = $50
(
    '10000000-0000-0000-0000-000000000003',
    '22222222-2222-2222-2222-222222222222',
    '11111111-1111-1111-1111-111111111111',
    'pending',
    1,
    50.00,
    'usd',
    NOW() + INTERVAL '30 minutes'   -- expires 30 min from insert time
);

-- Booking #1: 2 General tiered tickets
INSERT INTO booking_tiered_tickets (
    id,
    booking_id,
    ticket_tier_id,
    unit_price
)
VALUES
(
    '88888888-8888-8888-8888-888888888880',
    '10000000-0000-0000-0000-000000000001',
    '77777777-7777-7777-7777-777777777777',
    50.00
),
(
    '88888888-8888-8888-8888-888888888881',
    '10000000-0000-0000-0000-000000000001',
    '77777777-7777-7777-7777-777777777777',
    50.00
);

-- Booking #3: 1 General tiered ticket
INSERT INTO booking_tiered_tickets (
    id,
    booking_id,
    ticket_tier_id,
    unit_price
)
VALUES
(
    '88888888-8888-8888-8888-888888888882',
    '10000000-0000-0000-0000-000000000003',
    '77777777-7777-7777-7777-777777777777',
    50.00
);

-- Seated booking #2 occupies seats A1 and A2
INSERT INTO booking_seated_tickets (
    booking_id,
    seat_id
)
VALUES
(
    '10000000-0000-0000-0000-000000000002',
    'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa'
),
(
    '10000000-0000-0000-0000-000000000002',
    'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb'
);

-- Reflect the booked state on the seats themselves
UPDATE event_seats
SET is_available = FALSE
WHERE id IN (
    'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa',
    'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb'
);

-- Reflect the 3 booked tickets on the General tier (was 10000, now 9997)
UPDATE event_tiers
SET available_tickets = 9997
WHERE id = '77777777-7777-7777-7777-777777777777';

-- Reflect the booked open_field tickets: 3 of the 10000 are taken
UPDATE events
SET available_tickets = 9997
WHERE id = '11111111-1111-1111-1111-111111111111';

-- Reflect the booked seated tickets: 2 of the 1000 are taken
UPDATE events
SET available_tickets = 998
WHERE id = '22222222-2222-2222-2222-222222222222';


-- Also insert a pending payment
INSERT INTO payments (
    id,
    booking_id,
    stripe_checkout_session_id,
    stripe_checkout_url,
    stripe_payment_intent_id,
    amount_cents,
    currency,
    status
)
VALUES
(
    '10000000-0000-0000-0000-000000000001',
    '10000000-0000-0000-0000-000000000001',
    'cs_test_10000000000000000000000001',
    'https://...',
    NULL,
    10000,
    'usd',
    'pending'
),
(
    '10000000-0000-0000-0000-000000000002',
    '10000000-0000-0000-0000-000000000002',
    'cs_test_10000000000000000000000002',
    'https://...',
    NULL,
    30000,
    'usd',
    'pending'
);