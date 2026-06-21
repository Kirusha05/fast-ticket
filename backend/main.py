from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config.db_session import init_db_pool, close_db_pool

from routes.users import router as user_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # These will run on app startup
    await init_db_pool()
    yield
    # Everything here is for cleanup
    await close_db_pool()


app = FastAPI(lifespan=lifespan)

@app.get('/')
async def root():
    return {"message": "What's good bro???"}

@app.get('/health')
async def health():
    return {"status": "ok"}

app.include_router(user_router, prefix="/users")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Avoid wildcard * in prod
    allow_credentials=False,
    allow_methods=["*"],  # Open only necessary methods
    allow_headers=["Authorization", "Content-Type"]
)
# cannot use allow_credentials=True with allow_origins=["*"] in production. 
# The CORS specification forbids this combination. 
# When credentials are allowed, you must explicitly list the allowed origins

# Start with
# uv run alembic upgrade head
# uv run uvicorn main:app --host 0.0.0.0 --port 8000
# uv run uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4 --log-level error