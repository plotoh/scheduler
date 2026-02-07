# src/schemas/notification.py

from datetime import datetime, timezone
from typing import Optional, Any

import pytz
from pydantic import BaseModel, field_validator, ConfigDict, Field


class NotificationBase(BaseModel):
    user_id: int
    message: str = Field(..., min_length=10, max_length=200)
    channel: str = Field(default='email', pattern='^(email|sms|push)$')  # telegram vk голубем


class NotificationCreate(NotificationBase):
    send_at: datetime
    timezone: str = Field(default='UTC')

    @field_validator('send_at', mode='before')
    @classmethod
    def parse_datetime_string(cls, v: Any) -> Any:
        if isinstance(v, datetime):
            return v

        if isinstance(v, str):
            v = v.strip()
            formats = [
                "%Y-%m-%dT%H:%M:%S",
                "%Y-%m-%d %H:%M:%S",
                "%Y-%m-%d %H:%M",
                "%d.%m.%Y %H:%M:%S",
                "%d.%m.%Y %H:%M",
            ]

            for fmt in formats:
                try:
                    return datetime.strptime(v, fmt)
                except ValueError:
                    continue

            # Если ни один формат не подошел, парситься как ISO с временной зоной
            try:
                return datetime.fromisoformat(v.replace('Z', '+00:00'))
            except ValueError:
                raise ValueError(
                    f"Некорректный формат даты. Используйте стандартный для РФ формат")

        raise TypeError(f"Ожидается строка или datetime, получен {type(v)}")

    @field_validator('send_at')
    @classmethod
    def make_timezone_aware(cls, v: datetime) -> datetime:
        if v.tzinfo is None:
            return v.replace(tzinfo=timezone.utc)
        return v

    @field_validator('timezone')
    @classmethod
    def validate_timezone(cls, v: str) -> str:
        v = v.strip()
        if v.upper() == 'UTC':
            return 'UTC'

        try:
            pytz.timezone(v)
            return v
        except pytz.exceptions.UnknownTimeZoneError:
            raise ValueError(f"Неизвестный часовой пояс: {v}")


class NotificationUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    message: Optional[str] = Field(None, min_length=1, max_length=200)
    channel: Optional[str] = Field(None, pattern='^(email|sms|push)$')
    send_at: Optional[datetime] = None
    status: Optional[str] = Field(None, pattern='^(pending|sent|failed)$')

    @field_validator('send_at', mode='before')
    @classmethod
    def parse_datetime_string(cls, v: Any) -> Any:
        if v is None:
            return None
        return NotificationCreate.parse_datetime_string.__func__(v)


class NotificationResponse(NotificationBase):
    id: int
    send_at: datetime
    status: str
    timezone: str
    created_at: datetime
