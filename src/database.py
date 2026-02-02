# src/database.py
import asyncpg
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional

from src.config import DATABASE_URL


class Database:
    def __init__(self):
        self.__pool: Optional[asyncpg.Pool] = None

    async def create_pool(self):
        if self.__pool:
            return

        self.__pool = await asyncpg.create_pool(DATABASE_URL)  # добавить настройки пула

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
        # async with asyncpg.create_pool(DATABASE_URL, min_size=1, max_size=5) as pool:
        #     async with pool.acquire() as conn:
        async with self.connection() as conn:
            await conn.execute("\n"
                               "                CREATE TABLE IF NOT EXISTS users (\n"
                               "                                    id SERIAL PRIMARY KEY,\n"
                               "                                    email TEXT,\n"
                               "                                    phone_number TEXT,\n"
                               "                                )\n"
                               "                            ")

            await conn.execute("\n"
                               "                CREATE TABLE IF NOT EXISTS scheduled_notifications (\n"
                               "                                                    id SERIAL PRIMARY KEY,\n"
                               "                        user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,\n"
                               "                        message TEXT NOT NULL,\n"
                               "                        send_at TIMESTAMPTZ NOT NULL,\n"
                               "                        status TEXT NOT NULL CHECK (status IN ('pending', 'sent'))\n"
                               "                    )\n"
                               "                ")


db = Database()
"""решил инициализировать здесь, чтобы импортировать - это дает один экземпляр бд, простоту кода. наверное??? """


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
