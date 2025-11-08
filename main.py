# main.py
import asyncio

from models import NotificationDB
from scheduler import schedule, run_pending
from schemas import NotificationCreate


async def main():
    await NotificationDB.create_table()
    try:
        notif = NotificationCreate(
            user_id="123",
            message="Тестовое уведомление с часовым поясом",
            send_at="2025-10-30 14:30",  # строка парсится в таймстамп
            priority="normal"
        )
        await schedule(notif)
        print("Уведомление сохранено")
    except ValueError as ve:
        print(f"Ошибка при обработке уведомления: {ve}")
        return


# # main.py
# import asyncio
#
# from models import NotificationDB
# from scheduler import schedule, run_pending
# from schemas import NotificationCreate
#
#
# async def main():
#     await NotificationDB.create_table()
#     try:
#         notif = NotificationCreate(
#             user_id="123",
#             message="Тестовое уведомление с часовым поясом",
#             send_at="2025-10-30 14:30",  # строка парсится в таймстамп
#             priority="normal"
#         )
#         await schedule(notif)
#         print("Уведомление сохранено")
#     except ValueError as ve:
#         print(f"Ошибка при обработке уведомления: {ve}")
#         return
#
#     # Отправляем все "созревшие" уведомления
#     await run_pending()
#
# if __name__ == "__main__":
#     asyncio.run(main())