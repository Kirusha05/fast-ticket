-- Requires user.sql, event.sql and seats.sql to be loaded first

INSERT INTO bookings (
    id,
    user_id,
    event_id,
    status,
    ticket_count
)
VALUES
    -- user 1, open field event, 2 tickets
    (
        '10000000-0000-0000-0000-000000000001',
        '11111111-1111-1111-1111-111111111111',
        '11111111-1111-1111-1111-111111111111',
        'confirmed',
        2
    ),
    -- user 1, seated event, seats A1 + A2
    (
        '10000000-0000-0000-0000-000000000002',
        '11111111-1111-1111-1111-111111111111',
        '22222222-2222-2222-2222-222222222222',
        'confirmed',
        2
    ),
    -- user 2, open field event, 1 ticket
    (
        '10000000-0000-0000-0000-000000000003',
        '22222222-2222-2222-2222-222222222222',
        '11111111-1111-1111-1111-111111111111',
        'confirmed',
        1
    );

-- Seated booking #2 occupies seats A1 and A2
INSERT INTO booking_seats (
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
UPDATE seats
SET is_available = FALSE
WHERE id IN (
    'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa',
    'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb'
);

-- Reflect the booked open_field tickets: 3 of the 10000 are taken
UPDATE events
SET available_tickets = 9997
WHERE id = '11111111-1111-1111-1111-111111111111';

-- Reflect the booked seated tickets: 2 of the 1000 are taken
UPDATE events
SET available_tickets = 998
WHERE id = '22222222-2222-2222-2222-222222222222';