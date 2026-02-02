# main.py
import asyncio
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from typing import AsyncGenerator

import asyncpg
import uvicorn

from src.database import db
from src.service.scheduler import Scheduler
from fastapi import FastAPI
from src.api.notification import router as notif_router

"""
прописать аннотации
"""


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    try:
        await db.initialize()
        await db.init_tables()
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

app.include_router(notif_router)


if __name__ == "__main__":

    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
