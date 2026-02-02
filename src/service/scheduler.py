# src/service/scheduler.py

from datetime import datetime
import asyncpg

from src.schemas.notification import NotificationBase


class Scheduler:
    def __init__(self, connection: asyncpg.Connection):
        self.conn = connection

    async def add_notification(self, data: NotificationBase):
        user_id, message, send_at = data.user_id, data.message, data.send_at

        # добавить проверки на существование пользователя?? / корректность сообщения, таймстампа?

        # async with AsyncDB() as conn: # execute
        res = await self.conn.fetchrow("""
            INSERT INTO scheduled_notifications (user_id, message, send_at, status)
            VALUES ($1, $2, $3, 'pending')
            RETURNING id, user_id, message, send_at, status, created_at
        """, user_id, message, send_at)

        # добавить логгер - print(res, f"Запланировано: user_id={user_id}, время={send_at}")
        return dict(res) if res else {}

    async def get_notifications(
            self,
            user_id: int = None,
            status: str = 'pending'
    ):
        # async with AsyncDB() as conn:
        res = await self.conn.fetch("""
            SELECT * FROM scheduled_notifications
            WHERE user_id = $1 AND status = $2
            ORDER BY send_at DESC
            """, user_id, status)

        return [dict(row) for row in res]


async def run_pending(self, user_id: int):
    now = datetime.utcnow()
    # async with AsyncDB() as conn:
    # Получаем все просроченные pending
    rows = await self.conn.fetch("""
                SELECT id, user_id, message, send_at
                FROM scheduled_notifications
                WHERE user_id = $1 AND status = 'pending' AND send_at <= $2
                ORDER BY send_at 
            """, user_id, now)

    # if not rows:
    #     return {
    #         'success': f"[{datetime.now().isoformat()}] Нет уведомлений для отправки"
    #     }

    sent_count = 0
    for row in rows:
        """
        привязать классы отправления из сервиса
        """

        print(f"ОТПРАВКА → user_id={row['user_id']}: {row['message']}")
        await self.conn.execute("""
                UPDATE scheduled_notifications SET status = 'sent' WHERE id = $1
            """, row['id'])
        sent_count += 1

        return sent_count  # {'success': f"Обработано и помечено как sent: {sent_count} уведомлений"}
