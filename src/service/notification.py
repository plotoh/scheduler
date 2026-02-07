# src/service.notification.py
from abc import abstractmethod, ABC
from datetime import datetime, timezone
import asyncpg

from src.schemas.notification import NotificationBase


class DeliveryChannel(ABC):
    @abstractmethod
    def send(self, user_id: int, message: str):
        pass


class EmailChannel(DeliveryChannel):
    async def send(self, user_id: int, message: str):
        print(f"Sending EMAIL {message} to user with id {user_id}")


class SMSChannel(DeliveryChannel):
    async def send(self, user_id: int, message: str):
        print(f"Sending SMS {message} to user with id {user_id}")


class PushChannel(DeliveryChannel):
    async def send(self, user_id: int, message: str):
        print(f"Sending Push {message} to user with id {user_id}")


class Scheduler:
    channels = {
        "email": EmailChannel(),
        "sms": SMSChannel(),
        "push": PushChannel(),
    }

    def __init__(self, connection: asyncpg.Connection):
        self.conn = connection

    async def add_notification(self, data: NotificationBase):
        user_id, message, channel, send_at = data.user_id, data.message, data.channel, data.send_at

        # добавить проверки на существование пользователя?? / корректность сообщения, таймстампа?

        # async with AsyncDB() as conn: # execute
        res = await self.conn.fetchrow("""
            INSERT INTO scheduled_notifications (user_id, message, channel, send_at, status)
            VALUES ($1, $2, $3, $4, 'pending')
            RETURNING id, user_id, message, channel, send_at, status, created_at
        """, user_id, message, channel, send_at)

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
        now = datetime.now(timezone.utc)

        # Получаем уведомления вместе с каналом пользователя
        rows = await self.conn.fetch("""
                    SELECT id, user_id, message, send_at, channel
                    FROM scheduled_notifications
                    WHERE user_id = $1 AND status = 'pending' AND send_at <= $2
                    ORDER BY send_at 
                """, user_id, now)

        if not rows:
            return {
                'success': f"[{datetime.now().isoformat()}] Нет уведомлений для отправки"
            }

        # Проверяем, есть ли канал у пользователя
        user_channel = rows[0]['channel'] if rows else None
        channel_class = self.channels.get(user_channel, EmailChannel())

        # Отправляем уведомления
        for notification in rows:
            await channel_class.send(
                user_id=user_id,
                message=notification['message']
            )
            # Обновляем статус уведомления
            await self.conn.execute(
                "UPDATE scheduled_notifications SET status = 'sent' WHERE id = $1",
                notification['id']
            )

        return {
            'success': f"Отправлено {len(rows)} уведомлений через канал: {user_channel}",
            'channel': user_channel,
            'count': len(rows)
        }
