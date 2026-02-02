# main.py
import asyncio
from datetime import datetime, timedelta
from database import init_db
from src.service.scheduler import Scheduler
from fastapi import FastAPI
from src.api.notification import router as notif_router

'''
прописать:
БД
таблица пользователей (ид, мыло, номер, предпочитаемый способ уведов??) 

круды для нее !!!


 пидантик модели для уведов и (ответ уведомления, создание уведомления)
 сервис уведомлений и (запросы к бд - получение уведов по ид, добавление уведов с ид)

 конфиг дла аппа 
 подключение к бд
 создание 2ух таблиц
 
 сам апп (конфиг, бд, лайфспан)
 аутентификацию - login register logout ручки и сервис для них


добавить опцию отправления через смс пуш имэйл (хранить данные для пользователя в бд)

'''


app = FastAPI()


app.include_router(notif_router)


async def main():
    await init_db()
    scheduler = Scheduler()

    # Планируем уведомления
    now = datetime.utcnow()
    await scheduler.schedule(1, "Привет через 5 сек!", now + timedelta(seconds=5))
    await scheduler.schedule(2, "Встреча через 10 сек!", now + timedelta(seconds=10))
    await scheduler.schedule(3, "Это уже пора отправить!", now - timedelta(seconds=3))

    print("\nПланировщик запущен. Проверка каждые 3 секунды...\n")
    while True:
        await scheduler.run_pending()
        await asyncio.sleep(3)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nПланировщик остановлен пользователем")



# import asyncio
#
# from models import NotificationDB
# from scheduler import schedule, run_pending
# from schemas import NotificationCreate
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