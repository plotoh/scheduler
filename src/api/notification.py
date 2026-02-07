# src/api/notification.py
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, Response
import asyncpg

from src.schemas.notification import NotificationCreate, NotificationResponse
from src.service.notification import Scheduler
from src.dependencies import get_db

router = APIRouter(prefix="/notifications", tags=["Notifications"])


# при создании уведомления оно не подтягивается не откуда,требуется ручной ввод
@router.post('/',
             summary="Создание уведомления",
             description="Создание уведомления от пользователя")
async def create_notification(
        notif_data: NotificationCreate,
        conn: asyncpg.Connection = Depends(get_db),
        # response: Response,
        # user_id: int = Depends(get_user_id)) пока без авторизации
):
    try:
        scheduler = Scheduler(conn)
        res = await scheduler.add_notification(notif_data)
        # response.status_code = status.HTTP_201_CREATED
        # return res

    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Не удалось создать уведомление: " + str(e)
        )


@router.get('/',
            response_model=List[NotificationResponse],
            summary="Получить уведомления",
            description='Получение уведомлений из БД, пока что без авторизации')
async def get_user_notifications(
        # response: Response,
        # user_id: int = Depends(get_user_id),
        # пока без пагинации, offset limit
        user_id: int = None,
        notif_status: str = 'pending',
        conn: asyncpg.Connection = Depends(get_db)
):
    try:
        scheduler = Scheduler(conn)
        notifications = await scheduler.get_notifications(user_id=user_id, status=notif_status)
        return notifications
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при получении уведомлений: " + str(e)
        )