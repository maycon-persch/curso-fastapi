from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr


class Database(UserCreate):
    id: int


class UserList(BaseModel):
    users: list[UserResponse]


class Message(BaseModel):
    message: str
