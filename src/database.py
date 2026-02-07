# src/database.py
import asyncpg
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional

from src.config import settings


class Database:
    def __init__(self):
        self.__pool: Optional[asyncpg.Pool] = None

    async def create_pool(self):
        if self.__pool:
            return

        self.__pool = await asyncpg.create_pool(settings.DATABASE_URL)  # добавить настройки пула

    async def close(self):
        if self.__pool:
            await self.__pool.close()
            self.__pool = None

    @asynccontextmanager
    async def connection(self) -> AsyncGenerator[asyncpg.Connection, None]:
        if not self.__pool:
            await self.create_pool()
        async with self.__pool.acquire() as conn:
            yield conn

    async def init_db(self):
        async with self.connection() as conn:
            await conn.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        id SERIAL PRIMARY KEY,
                        username TEXT NOT NULL UNIQUE,
                        password TEXT NOT NULL,
                        email TEXT UNIQUE,
                        phone_number TEXT UNIQUE,
                        created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
                    )
                """)

            await conn.execute("""
                CREATE TABLE IF NOT EXISTS scheduled_notifications (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                    message TEXT NOT NULL,
                    channel VARCHAR(20) NOT NULL DEFAULT 'email',
                    send_at TIMESTAMP NOT NULL,
                    status VARCHAR(20) NOT NULL DEFAULT 'pending' 
                        CHECK (status IN ('pending', 'sent', 'failed')),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            await conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_notifs_user_status 
                ON scheduled_notifications(user_id, status);
            """)


db = Database()

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
