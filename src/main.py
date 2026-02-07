# main.py
import asyncio
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from typing import AsyncGenerator

import asyncpg
import uvicorn

from src.database import db
from src.service.notification import Scheduler
from fastapi import FastAPI
from src.api import main_router

"""
прописать аннотации

прописать авторизацию

прописать добавление пользователя в бд

прописать взаимодействие таблиц друг с другом

прописать проверку на существование пользователя
"""


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    try:
        await db.create_pool()
        await db.init_db()
        # await asyncio.gather(db.create_pool(), db.init_db())

        yield

        await db.close()
    except Exception as e:
        print(f"Ошибка при запуске приложения: {str(e)}")  # logger
        raise  # написать эксепшн??

app = FastAPI(
    title="Notification API",
    lifespan=lifespan
)

app.include_router(main_router)


if __name__ == "__main__":

    uvicorn.run(
        "src.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
    )


