from psycopg_pool import AsyncConnectionPool
from psycopg.rows import dict_row
from config import config

"""
Can also set these in Postgres
ALTER SYSTEM SET idle_session_timeout = '2min'
ALTER SYSTEM SET idle_in_transaction_session_timeout = '10s';
SELECT pg_reload_conf();

Check with
SELECT name, setting, unit, source FROM pg_settings WHERE name = 'idle_session_timeout';
SELECT name, setting, unit, source FROM pg_settings WHERE name = 'idle_in_transaction_session_timeout';
"""


DB_POOL = None

async def init_db_pool():
    global DB_POOL

    try:
        print("Creating DB connnection pool")
        print(f"min_size={config.DB.POOL_MIN_SIZE}")
        print(f"max_size={config.DB.POOL_MAX_SIZE}")
        # Important rule: max_size * number_of_app_instances < PostgreSQL max_connections
        DB_POOL = AsyncConnectionPool(
            conninfo=config.DB.connection_string,
            min_size=config.DB.POOL_MIN_SIZE,
            max_size=config.DB.POOL_MAX_SIZE,
            open=False, # Don't open immediately, we'll open in lifespan
            max_idle=60,       # kill conn if idle 60s
            max_lifetime=300,   # kill conn after 5 minutes no matter what, refreshing them
            kwargs={
                "prepare_threshold": None
            }
        )
        await DB_POOL.open()
        await DB_POOL.wait(config.DB.POOL_CREATION_TIMEOUT)
        print("Postgres connection established")
    except Exception as e:
        raise RuntimeError("Failed to initialize DB pool", e)

async def close_db_pool():
    if DB_POOL:
        await DB_POOL.close()

async def get_db_session():
    if DB_POOL is None:
        raise RuntimeError("DB pool not initialized")

    async with DB_POOL.connection() as conn:
        try:
            conn.row_factory = dict_row
            yield conn
            await conn.commit()  # Auto-commit if no exception
        except Exception:
            await conn.rollback()
            raise