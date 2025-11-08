# models.py
import asyncpg
from datetime import date
from db import get_pool


class NotificationDB:
    @staticmethod
    async def create_table():
        """Создаёт таблицу, если не существует"""
        pool = await get_pool()
        async with pool.acquire() as conn:
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS scheduled_notifications (
                    id SERIAL PRIMARY KEY,
                    user_id VARCHAR(10) NOT NULL,
                    message TEXT NOT NULL,
                    send_at TIMESTAMPTZ NOT NULL,
                    status VARCHAR(10) NOT NULL DEFAULT 'pending',
                    priority VARCHAR(10) NOT NULL DEFAULT 'normal',
                    CHECK (status IN ('pending', 'sent')),
                    CHECK (priority IN ('low', 'normal', 'high'))
                )
            """)

    @staticmethod
    async def add_notification(user_id: str, message: str, send_at: date, priority: str = 'normal'):
        pool = await get_pool()
        async with pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO scheduled_notifications (user_id, message, send_at, priority)
                VALUES ($1, $2, $3, $4)
                """,
                user_id, message, send_at, priority
            )

    @staticmethod
    async def get_pending_due() -> list[asyncpg.Record]:
        pool = await get_pool()
        async with pool.acquire() as conn:
            return await conn.fetch(
                """
                SELECT id, user_id, message, send_at, priority
                FROM scheduled_notifications
                WHERE status = 'pending' AND send_at <= NOW()
                """
            )

    @staticmethod
    async def mark_as_sent(notification_id: int):
        pool = await get_pool()
        async with pool.acquire() as conn:
            await conn.execute(
                "UPDATE scheduled_notifications SET status = 'sent' WHERE id = $1",
                notification_id
            )

    @staticmethod
    async def mark_all_as_pending():
        pool = await get_pool()
        async with pool.acquire() as conn:
            await conn.execute(
                "UPDATE scheduled_notifications SET status = 'pending' WHERE status = 'sent'")

    @staticmethod
    async def clear_all_notifications_for_testing():
        pool = await get_pool()
        async with pool.acquire() as conn:
            await conn.execute(
                "DELETE FROM scheduled_notifications")

    @staticmethod
    async def get_all_notifications():
        pool = await get_pool()
        async with pool.acquire() as conn:
            return await conn.fetch(
                "SELECT * FROM scheduled_notifications")