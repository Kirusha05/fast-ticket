import psycopg
from config import config

if not config.DB.DATABASE.endswith("_test"):
    raise RuntimeError("DB_DATABASE name must end with _test")

with psycopg.connect(config.DB.connection_string) as conn:
    models = [
        "tickets",
        "payments",
        "booking_tiered_tickets",
        "booking_seated_tickets",
        "event_tiers",
        "event_seats",
        "bookings",
        "events",
        "users"
    ]
    for model in models:
        try:
            conn.execute(f"DELETE FROM {model}")
        except:
            continue
    conn.commit()

    print("\n--- Teardown done ---\n")