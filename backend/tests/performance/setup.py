import psycopg
from config import config

if not config.DB.DATABASE.endswith("_test"):
    raise RuntimeError("DB_DATABASE name must end with _test")

with psycopg.connect(config.DB.connection_string) as conn:
    with open('tests/performance/data/users.sql') as f:
        conn.execute(f.read())
    with open('tests/performance/data/events.sql') as f:
        conn.execute(f.read())
    with open('tests/performance/data/tiers.sql') as f:
        conn.execute(f.read())
        conn.commit()

    print("\n--- Setup done ---\n")