from typing import Optional, Dict, Any, List, Union
import asyncpg


class Auth:
    ALLOWED_SEARCH_FIELDS = {
        'id': int,
        'username': str,
        'email': str,
        'phone_number': str
    }

    def __init__(self, conn: asyncpg.Connection):
        self.conn = conn

    async def get_user_by_field(
            self,
            field_name: str,
            field_value: Union[int, str]
    ) -> Optional[Dict[str, Any]]:

        allowed_fields = self.ALLOWED_SEARCH_FIELDS
        expected_type = allowed_fields[field_name]

        if field_name not in allowed_fields:
            raise ValueError(
                f"Поле '{field_name}' не разрешено для поиска. "
                f"Разрешенные поля: {', '.join(allowed_fields.keys())}"
            )

        if not isinstance(field_value, expected_type):
            raise TypeError(
                f"Для столбца '{field_name}' ожидается тип {expected_type.__name__}, "
                f"получен {type(field_value).__name__}"
            )

        query = f"SELECT * FROM users WHERE {field_name} = $1"
        row = await self.conn.fetchrow(query, field_value)

        return dict(row) if row else None

    async def create_user(self, username: str, password: str, email: str, phone_number: str) -> Dict[str, Any]:
        # async with self.conn.acquire() as conn:
        row = await self.conn.fetchrow("""
                INSERT INTO users (username, password, email, phone_number)
                VALUES ($1, $2, $3, $4)
                RETURNING *
            """, username, password, email, phone_number)
        return dict(row)
