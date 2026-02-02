# src/schemas/notification.py

from datetime import datetime, timezone
from typing import Optional
from pydantic import BaseModel, field_validator, ConfigDict, Field


class NotificationBase(BaseModel):
    user_id: int
    message: str = Field(..., min_length=10, max_length=200)
    send_at: datetime
    # priority: Literal['low', 'normal', 'high'] = 'normal'

    # мне не нравится обработка в цикле, думаю над лучшим вариантом
    @field_validator('send_at', mode='before')
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
            for fmt in formats:
                try:
                    dt = datetime.strptime(value, fmt)
                    return cls.__check_timezone(dt)
                except ValueError:
                    continue
            raise ValueError(f"Не удалось распарсить время: {value}")

        # type(send_at) - datetime
        elif isinstance(value, datetime):
            return cls.__check_timezone(value)

        # type(send_at) - неподдерживаемый тип
        raise ValueError(f"Для send_at ожидался str или datetime, получено: {type(value).__name__}")

    @staticmethod
    def __check_timezone(value):
        return value if value.tzinfo else value.replace(tzinfo=timezone.utc)

    model_config = ConfigDict(frozen=True)  # превращает уведомление в неизменяемый объект


class NotificationCreate(NotificationBase):
    pass


class NotificationResponse(NotificationBase):
    id: int
    status: str
    created_at: Optional[datetime] = None



# class NotificationResponse(NotificationBase):
#     id: int

