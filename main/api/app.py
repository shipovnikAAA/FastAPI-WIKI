from fastapi import FastAPI, Depends, HTTPException, status
from main.routers import data, users
from migration.database.create_tables import (
    create_titles_table,
    create_texts_table,
    create_permisions_table,
    create_users_table,
)
from main.core.logger import setup_logging
from contextlib import asynccontextmanager
from logging import getLogger
from main.core.config import JWT_CONFIG, APP_CONFIG
# from migration.database.admin import create_Sadovnikov_user
from fastapi.middleware.cors import CORSMiddleware
from main.models.database import init_pool_data, close_pool_data

logger = getLogger(__name__)

tags_metadata = [
    {
        "name": "data",
        "description": "API for work with **data get or init new**",
    },
    {
        "name": "users",
        "description": "API for work with **users data**",
    },
]

description = """
# (👉ﾟヮﾟ)👉       SIGNAL API helps you do awesome stuff ✨⭐✨     👈(ﾟヮﾟ👈)
"""

app_state = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Обработчик жизненного цикла приложения."""
    setup_logging("API")
    logger.info("Starting lifespan...")
    await init_pool_data()
    await create_titles_table()
    await create_texts_table()
    await create_users_table()
    await create_permisions_table()
    yield
    logger.info("Stopping lifespan...")
    await close_pool_data()

APP = FastAPI(
    title="SIGNAL API (❤️ ω ❤️)",
    description=description,
    root_path="/api",
    summary="API for work with signal eco-system",
    version="0.0.1",
    contact={
        "name": "Shipovskii Alexander",
        "url": r"http://t.me/signal_safety",
        "email": "shipovniktuklosaw@gmail.com",
    },
    openapi_tags=tags_metadata,
    swagger_ui_parameters={"syntaxHighlight": {"theme": "obsidian"}},
    lifespan=lifespan,
)

# Настраиваем CORS с учетом HTTPS
APP.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В продакшене заменить на конкретные домены
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

APP.include_router(
    users.router,
)

APP.include_router(
    data.router,
)