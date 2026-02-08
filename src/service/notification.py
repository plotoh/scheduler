# src/service.notification.py
from abc import abstractmethod, ABC
from datetime import datetime, timezone
from typing import List

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

    async def add_notification(self, data: NotificationBase) -> dict:
        user_exists = await self.conn.fetchval(
            "SELECT EXISTS(SELECT 1 FROM users WHERE id = $1)",
            data.user_id
        )

        if not user_exists:
            raise ValueError(f"Пользователь с ID {data.user_id} не найден")

        if data.send_at < datetime.now():
            raise ValueError("Дата отправки не может быть в прошлом")

        result = await self.conn.fetchrow("""
                  INSERT INTO scheduled_notifications 
                  (user_id, message, channel, send_at, status)
                  VALUES ($1, $2, $3, $4, 'pending')
                  RETURNING 
                      id, user_id, message, channel, send_at, 
                      status, created_at
              """,
                                          data.user_id, data.message, data.channel, data.send_at)

        return dict(result) if result else {}
        # добавить логгер - print(res, f"Запланировано: user_id={user_id}, время={send_at}")

    async def get_notifications(
            self,
            user_id: int = None,
            status: str = 'pending'
    )-> List[dict]:

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

        sent_count = 0

        for row in rows:
            channel_name = row["channel"]
            channel_class = self.channels.get(channel_name)

            if not channel_class:
                print(f"Неизвестный канал: {channel_name} → пропускаем")
                continue

            await channel_class.send(user_id, row["message"])

            await self.conn.execute(
                "UPDATE scheduled_notifications SET status = 'sent' WHERE id = $1",
                row["id"]
            )
            sent_count += 1

        return {
            "success": f"Отправлено {sent_count} уведомлений",
            "count": sent_count
        }
