from enum import StrEnum
from pydantic_settings import BaseSettings, SettingsConfigDict
import os


class Mode(StrEnum):
    LOCAL = 'local'
    TEST = 'test'
    DEV = 'dev'
    PROD = 'prod'
    CLOUD = 'cloud'
    LOAD_TEST = 'load_test'


_MODE_TO_ENVFILE = {
    Mode.LOCAL: '.env',
    Mode.TEST: '.env.test',
    Mode.PROD: '.env.prod',
    Mode.DEV: '.env.dev',
    Mode.LOAD_TEST: '.env.test'
}


def get_environment() -> Mode:
    mode = os.getenv('MODE', 'local').upper()

    try:
        environment = Mode[mode]
        return environment
    except KeyError:
        raise ValueError(f'Invalid mode: {mode}')


def load_environment_from_file() -> str | None:
    environment_mode = get_environment()

    if environment_mode == Mode.CLOUD:
        print("Running in cloud environmemt, skipping .env files")
        # When env_file=None, Pydantic will read directly from your environment variables
        return None
    
    filename = _MODE_TO_ENVFILE[environment_mode]
    print(f'Trying to load config from {filename}')

    if not os.path.exists(filename):
        raise RuntimeError(f"File {filename} not found")
    return filename


class DBConfig(BaseSettings):
    HOST: str = "localhost"
    PORT: int = 5432
    DATABASE: str = "postgres"
    USER: str = "postgres"
    PASSWORD: str = "postgres"
    POOL_MIN_SIZE: int = 5
    POOL_MAX_SIZE: int = 20
    POOL_CREATION_TIMEOUT: int = 5 # seconds to wait for the pool to be available
    SSL: bool = False

    model_config = SettingsConfigDict(
        env_prefix="DB_",
        # When env_file=None, Pydantic will read directly from your environment variables
        env_file=load_environment_from_file(),
        extra="ignore",
    )

    @property
    def connection_string(self) -> str:
        ssl_mode = "?sslmode=require" if self.SSL else ""
        return f"postgresql://{self.USER}:{self.PASSWORD}@{self.HOST}:{self.PORT}/{self.DATABASE}{ssl_mode}"


class Auth0Config(BaseSettings):
    AUDIENCE: str = "https://your-api-identifier"
    DOMAIN: str = "your-tenant.auth0.com"
    CLIENT_ID: str = "your_client_id"
    CLIENT_SECRET: str = "your_client_secret"

    model_config = SettingsConfigDict(
        env_prefix="AUTH0_",
        env_file=load_environment_from_file(),
        extra="ignore",
    )


class StripeConfig(BaseSettings):
    SECRET_KEY: str = "dummy"
    PUBLISHABLE_KEY: str = "dummy"
    WEBHOOK_SECRET: str = "dummy"
    CURRENCY: str = "dummy"
    SUCCESS_URL: str = "dummy"
    CANCEL_URL: str = "dummy"

    model_config = SettingsConfigDict(
        env_prefix="STRIPE_",
        env_file=load_environment_from_file(),
        extra="ignore",
    )


class Config(BaseSettings):
    MODE: Mode = get_environment()
    DB: DBConfig = DBConfig()
    AUTH0: Auth0Config = Auth0Config()
    STRIPE: StripeConfig = StripeConfig()
    BOOKING_RESERVATION_TTL_HOURS: int = 2  # 1+ hours (at least 30 min, required by Stripe checkout expires_at)

    model_config = SettingsConfigDict(
        env_file=load_environment_from_file(),
        extra="ignore",
    )


config = Config()
print(f"Config.MODE = {config.MODE}")