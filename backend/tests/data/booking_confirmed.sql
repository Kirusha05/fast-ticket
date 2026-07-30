-- Requires user.sql, event.sql and tiers.sql to be loaded first

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
    -- user 1, tiered event, 2 General tickets @ $50 each = $100
    (
        '10000000-0000-0000-0000-000000000001',
        '11111111-1111-1111-1111-111111111111',
        '11111111-1111-1111-1111-111111111111',
        'confirmed',
        2,
        100.00,
        'usd',
        NOW()
    ),
    -- user 1, seated event, seats A1 + A2 @ $150 each = $300
    (
        '10000000-0000-0000-0000-000000000002',
        '11111111-1111-1111-1111-111111111111',
        '22222222-2222-2222-2222-222222222222',
        'confirmed',
        2,
        300.00,
        'usd',
        NOW()
    ),
    -- user 2, tiered event, 1 General ticket @ $50 = $50
    (
        '10000000-0000-0000-0000-000000000003',
        '22222222-2222-2222-2222-222222222222',
        '11111111-1111-1111-1111-111111111111',
        'confirmed',
        1,
        50.00,
        'usd',
        NOW()
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

-- Reflect the booked tiered tickets: 3 of the 10000 are taken
UPDATE events
SET available_tickets = 9997
WHERE id = '11111111-1111-1111-1111-111111111111';

-- Reflect the booked seated tickets: 2 of the 1000 are taken
UPDATE events
SET available_tickets = 998
WHERE id = '22222222-2222-2222-2222-222222222222';