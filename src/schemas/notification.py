# src/schemas/notification.py

from datetime import datetime, timezone
from typing import Optional, Any

import pytz
from pydantic import BaseModel, field_validator, ConfigDict, Field


class NotificationBase(BaseModel):
    model_config = ConfigDict(json_schema_extra={
            "example": {
                "user_id": 1,
                "message": "Напоминание о встрече",
                "channel": "email",
                "send_at": "2026-02-15T14:30:00"
            }
        })

    user_id: int
    message: str = Field(..., min_length=10, max_length=200)
    channel: str = Field(default='email', pattern='^(email|sms|push)$')  # telegram vk голубем
    send_at: datetime


class NotificationCreate(NotificationBase):
    pass


class NotificationResponse(NotificationBase):
    id: int
    status: str = Field("pending", pattern="^(pending|sent|failed)$")
    created_at: Optional[datetime] = None  # может быть null в БД???
