# scheduler.py
import asyncio
from schemas import NotificationCreate
from models import NotificationDB


# если понадобятся настройки, работа с состояниями уведомлений, объекта - верну класс. пока не вижу смысла
# class Schedule:
#     @staticmethod
async def schedule(notif: NotificationCreate):
    if isinstance(notif, NotificationCreate):
        await NotificationDB.add_notification(
            user_id=notif.user_id,
            message=notif.message,
            send_at=notif.send_at,
            priority=notif.priority
        )
        print(f"Уведомление сохранено для {notif.user_id}")

    # @staticmethod


async def run_pending():
    pending = await NotificationDB.get_pending_due()
    for row in pending:
        print(f'Sending: "{row["message"]}" to {row["user_id"]} at {row["send_at"]}')
        await NotificationDB.mark_as_sent(row["id"])
