from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str


class UserPut(BaseModel):
    name: str | None = None
    email: EmailStr | None = None
    password: str | None = None


class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr

    model_config = ConfigDict(from_attributes=True)


class UserList(BaseModel):
    users: list[UserResponse]


class Message(BaseModel):
    message: str


class Token(BaseModel):
    access_token: str
    token_type: str


class FilterPage(BaseModel):
    pagina: int = Field(ge=0, default=0)


class Admin(BaseModel):
    name: str
    email: EmailStr
    password: str
