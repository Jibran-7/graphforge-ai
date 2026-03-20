from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import api_router
from app.core.config import get_settings
from app.core.logging import get_logger, init_logging
from app.db.database import create_db_and_tables
import app.db.models  # noqa: F401

settings = get_settings()
log_level = "DEBUG" if settings.app_env.lower() == "development" else "INFO"
init_logging(level=log_level)
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI):
    Path(settings.upload_dir).mkdir(parents=True, exist_ok=True)
    create_db_and_tables()

    logger.info(
        "Starting %s in %s on %s:%s",
        settings.app_name,
        settings.app_env,
        settings.app_host,
        settings.app_port,
    )
    logger.info("Upload directory ready at %s", settings.upload_dir)
    logger.info("API routers registered: health, documents, graph, query")
    yield
    logger.info("Shutting down %s", settings.app_name)


def create_app() -> FastAPI:
    app = FastAPI(title=settings.app_name, lifespan=lifespan)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://127.0.0.1:5173", "http://localhost:5173"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(api_router)
    return app


app = create_app()
