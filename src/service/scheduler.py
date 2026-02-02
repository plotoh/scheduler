# scheduler.py

from datetime import datetime
from db import AsyncDB
from src.schemas import NotificationBase


class Scheduler:
    async def schedule(self, notification_data: NotificationBase):
        user_id, message, send_at = notification_data.user_id, notification_data.message, notification_data.send_at

        async with AsyncDB() as conn:
            res = await conn.execute("""
                INSERT INTO scheduled_notifications (user_id, message, send_at, status)
                VALUES ($1, $2, $3, 'pending')
            """, user_id, message, send_at)

            print(res, f"Запланировано: user_id={user_id}, время={send_at}")
            return dict(res)

    async def get_notifications(self, user_id: int = None, status: str = 'pending'):
        async with AsyncDB() as conn:
            res = await conn.fetch("""
            SELECT * FROM scheduled_notifications
            WHERE user_id = $1 AND status = $2
            ORDER BY send_at ASC
            """, user_id, status)

            return res

    async def run_pending(self, user_id: int):
        now = datetime.utcnow()
        async with AsyncDB() as conn:
            # Получаем все просроченные pending
            rows = await conn.fetch("""
                SELECT id, user_id, message, send_at
                FROM scheduled_notifications
                WHERE user_id = $1 AND status = 'pending' AND send_at <= $2
                ORDER BY send_at
            """, user_id, now)

            if not rows:
                print(f"[{datetime.now().isoformat()}] Нет уведомлений для отправки")
                return

            sent_count = 0
            for row in rows:
                print(f"ОТПРАВКА → user_id={row['user_id']}: {row['message']}")
                await conn.execute("""
                    UPDATE scheduled_notifications SET status = 'sent' WHERE id = $1
                """, row['id'])
                sent_count += 1

            print(f"Обработано и помечено как sent: {sent_count} уведомлений")
