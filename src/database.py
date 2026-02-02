# src/database\database.py
import asyncpg
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional

from src.config import DATABASE_URL

# от класса избавился т.к. антипаттерн, одинкласс отвечает за пул, подключение, нам не надо хранить состояние


class Database:
    def __init__(self):
        self.__pool: Optional[asyncpg.Pool] = None

    async def create_pool():



async def init_db():
    async with asyncpg.create_pool(DATABASE_URL, min_size=1, max_size=5) as pool:
        async with pool.acquire() as conn:
            await conn.execute("""
                            CREATE TABLE IF NOT EXISTS users (
                                id SERIAL PRIMARY KEY,
                                email TEXT,
                                phone_number TEXT,
                            )
                        """)

            await conn.execute("""
                CREATE TABLE IF NOT EXISTS scheduled_notifications (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                    message TEXT NOT NULL,
                    send_at TIMESTAMPTZ NOT NULL,
                    status TEXT NOT NULL CHECK (status IN ('pending', 'sent'))
                )
            """)


# Контекстный менеджер для подключения
# class AsyncDB:
#     async def __aenter__(self):
#         self.pool = await asyncpg.create_pool(DATABASE_URL, min_size=1, max_size=5)
#         self.conn = await self.pool.acquire()
#         return self.conn
#
#     async def __aexit__(self, exc_type, exc, tb):
#         await self.pool.release(self.conn)
#         await self.pool.close()
