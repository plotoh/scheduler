# schemas.py
from datetime import datetime, timezone
from typing import Literal
from pydantic import BaseModel, field_validator, ConfigDict


# решил вместо просто изменения обработки даты на дату и время прикрутить pydantic
class NotificationCreate(BaseModel):
    user_id: str
    message: str
    send_at: datetime
    priority: Literal['low', 'normal', 'high'] = 'normal'

    @field_validator('send_at', mode='before')  # выполнить эту функцию до стандартной валидации поля send_at
    @classmethod
    def parse_send_at(cls, value) -> datetime:
        """
        парсит строку в таймстамп с часовым поясом
        """
        # type(send_at) - строка
        if isinstance(value, str):
            formats = [
                "%Y-%m-%d %H:%M",
                "%Y-%m-%d %H:%M:%S%z",
                "%Y-%m-%d %H:%M:%S",
                "%Y-%m-%d %H:%M%z",
                "%Y-%m-%d",
                "%d/%m/%Y %H:%M",
                "%d.%m.%Y %H:%M",
                "%d-%m-%Y %H:%M",
                "%Y/%m/%d %H:%M",
                "%B %d, %Y %H:%M",
                "%b %d, %Y %H:%M",
                "%d %B %Y %H:%M",
                "%d %b %Y %H:%M",
            ]
            for fmt in formats:  # мне не нравится обработка в цикле, думаю над лучшим вариантом
                try:
                    dt = datetime.strptime(value, fmt)
                    return cls.__check_timezone(dt)
                except ValueError:
                    continue
            raise ValueError(f"Не удалось распарсить время: {value}")

        # type(send_at) - datetime
        if isinstance(value, datetime):
            return cls.__check_timezone(value)

        # type(send_at) - неподдерживаемый тип
        raise ValueError(f"Для send_at ожидался str или datetime, получено: {type(value).__name__}")

    @staticmethod
    def __check_timezone(value):
        return value if value.tzinfo else value.replace(tzinfo=timezone.utc)

    model_config = ConfigDict(frozen=True)  # превращает уведомление в неизменяемый объект
