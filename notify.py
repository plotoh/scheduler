import ara
import datetime as dt


# добавить обработку времени

class Notification:
    DATE_FORMATS = [
        "%Y-%m-%d",  # 2025-10-28
        "%d/%m/%Y",  # 28/10/2025
        "%d.%m.%Y",  # 28.10.2025
        "%d-%m-%Y",  # 28-10-2025
        "%Y/%m/%d",  # 2025/10/28
        "%B %d, %Y",  # October 28, 2025
        "%b %d, %Y",  # Oct 28, 2025
        "%d %B %Y",  # 28 October 2025
        "%d %b %Y",  # 28 Oct 2025
    ]

    def __init__(self, user_id: str, notification: tuple[str, str | dt.date, str | None] = None):
        self.user_id = user_id
        self.message, self.send_at, self.priority = None, None, None
        try:
            self.get_notification(notif=notification)
        except ValueError as ve:
            print(f'Не удалось создать уведомление. Ошибка: {ve}')

    def get_notification(self, notif=None):
        if not isinstance(notif, tuple) and len(notif) in [2, 3]:
            raise ValueError(f"Неверное уведомление {notif}")

        if len(notif) == 2:
            msg, send_at = notif
            priority = 'normal'
        else:
            msg, send_at, priority = notif

        if not isinstance(msg, str):
            raise ValueError(f"Уведомление {msg} не является строкой")

        if isinstance(send_at, dt.date):
            parsed_date = send_at
        elif isinstance(send_at, str):
            parsed_date = self.parse_date_string(send_at)
            if parsed_date is None:
                raise ValueError(f"Неверный формат даты: {send_at}")
        else:
            raise ValueError(f"Неверный формат даты: {send_at}")

        self.message, self.send_at, self.priority = msg, parsed_date, priority

    def parse_date_string(self, date_str: str) -> dt.date | None:
        """
        парсит строку в дату
        возвращает объект date или None, если формат не распознан.
        """
        for fmt in self.DATE_FORMATS:
            try:
                return dt.datetime.strptime(date_str, fmt).date()
            except ValueError:
                continue
        return


class Schedule:
    UID = 1

    def __init__(self):
        self.notifications = []

    def schedule(self, notif: Notification):
        if isinstance(notif, Notification):
            notif_dct = {
                'id': self.UID,
                'user_id': notif.user_id,
                'message': notif.message,
                'send_at': notif.send_at,
                'priority': notif.priority
            }
            self.notifications.append(notif_dct)
            Schedule.UID += 1

    def run_pending(self):
        print('INFO: отправка уведомлений')
        today = dt.date.today()
        for notif in self.notifications:
            send_at = notif['send_at']
            if send_at and send_at <= today:
                message = notif['message']
                if message:
                    print(
                        f'INFO: Sending message: "{message}" with priority: {notif['priority']}, with datetime {send_at} to user with id: {notif['user_id']}')
                else:
                    print("уведомления нет. не знаю почему. но мы разберемся. наверное")
            else:
                continue


notif1 = Notification("123", ("вот нахуя я так усложнил", "2025-10-28", 'normal'))
# print(notif.date)  # 2025-10-28
notif2 = Notification("124", ("вот нахуя я так усложнил", "2025-11-28"))
# print(notif.date)  # 2025-10-28

schedule = Schedule()
schedule.schedule(notif1)
schedule.schedule(notif2)
schedule.run_pending()
