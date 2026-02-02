# notif_api.py
from typing import List

from fastapi import Depends, Response, APIRouter, HTTPException, status


from src.schemas import NotificationBase
from src.scheduler import Scheduler

router = APIRouter(prefix="/notifications", tags=["Notifications"])

@router.post('/',
             summary="Создание уведомления",
             description="Создание уведомления от пользователя")
async def create_notification(
        notif_data: NotificationBase,
        response: Response
        # user_id: int = Depends(get_current_user_id)) пока без авторизации
    ):
    scheduler = Scheduler()
    try:
        res = await scheduler.schedule(notif_data)
        response.status_code = status.HTTP_201_CREATED
        return res

    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get('/',
            response_model=List[NotificationBase],
            summary="Получить уведомления",
            description='Получение уведомлений из БД, пока что без авторизации')
async def get_user_notifications(
        response: Response,
        # user_id: Optional[int] = Depends(get_current_user_id),
        user_id: int = None,
        notif_status: str = 'pending',
        # пока без пагинации, offset limit
        ):
        scheduler = Scheduler()
        try:
            res = await scheduler.get_notifications(user_id=user_id, status=notif_status)
            response.status_code = status.HTTP_200_OK
            return res




