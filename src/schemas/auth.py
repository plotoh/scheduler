from pydantic import BaseModel, Field, EmailStr, field_validator


class UserSchema(BaseModel):
    username: str = Field(..., min_length=5, max_length=50, examples=['cool_username'])
    password: str = Field(..., min_length=8, max_length=100, examples=['cool_password'])


class UserRegisterSchema(UserSchema):
    email: EmailStr = Field(examples=['email@mylo.omyl'])
    phone: str = Field(..., description="Номер телефона в формате +7XXXXXXXXXX", examples=['89991234567', '+7999 123 45 67'])

    @field_validator('phone')
    @classmethod
    def phone_validator(cls, phone: str = None):
        if isinstance(phone, str):
            if phone[0] == '8' or phone[0] == '7':
                normalized_number = ''.join(s for s in phone[1:] if s.isdigit())
            elif phone[:2] == '+7':
                normalized_number = ''.join(s for s in phone[2:] if s.isdigit())
            else:
                raise ValueError('В данный момент поддерживаются только номера из РФ и КЗ. '
                                 'Введенный номер %sph не допустим' % phone)

            if len(normalized_number) == 10:
                resulted_number = '+7' + normalized_number
                return resulted_number
            else:
                raise ValueError('Введен номер с некорректной длиной: %sph' % phone)
        raise TypeError('Введен номер некорректного типа данных: %sph' % phone)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class UserResponse(BaseModel):
    id: int
    username: str
    email: str