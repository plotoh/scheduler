# src/dependencies.py
from typing import AsyncGenerator
import asyncpg
from fastapi import Request, Depends

from src.database import db


# зависимость БД для ручек
async def get_db() -> AsyncGenerator[asyncpg.Connection, None]:
    async with db.connection() as conn:
        yield conn
