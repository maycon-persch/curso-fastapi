from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_session
from app.models import User
from app.schemas import (
    FilterPage,
    Message,
    UserCreate,
    UserList,
    UserPut,
    UserResponse,
)
from app.security import (
    get_current_user,
    get_password_hash,
)

Crud_Router = APIRouter(prefix="/users", tags=["Users teste do curso "])

T_Session = Annotated[Session, Depends(get_session)]
CurrentUser = Annotated[User, Depends(get_current_user)]


@Crud_Router.post(
    "/create", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
def post_user(user: UserCreate, session: T_Session):

    db_user = session.scalar(
        select(User).where(
            (User.username == user.username) | (User.email == user.email)
        )
    )
    if db_user:
        if db_user.username == user.username:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Esse nome de usuario ja está em uso!",
            )
        elif db_user.email == user.email:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Esse email ja está em uso!",
            )

    db_user = User(
        username=user.username,
        email=user.email,
        password=get_password_hash(user.password),
    )
    session.add(db_user)
    session.commit()
    session.refresh(db_user)

    return db_user


@Crud_Router.get("/get/id", status_code=status.HTTP_200_OK)
def get_id(
    current_user: CurrentUser,
):
    return {"id": current_user.id}


@Crud_Router.get(
    "/Read", response_model=UserList, status_code=status.HTTP_200_OK
)
def get_user(
    session: T_Session,
    current_user: CurrentUser,
    pagina: Annotated[FilterPage, Query()],
):
    users = session.scalars(select(User).limit(10).offset(pagina * 10))
    return {"users": users}


@Crud_Router.put(
    "/Update/{user_id}",
    status_code=status.HTTP_200_OK,
    response_model=UserResponse,
)
def update_user(
    user: UserPut,
    user_id: int,
    session: T_Session,
    current_user: CurrentUser,
):

    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você não possui permissão",
        )

    if username := user.username:
        current_user.username = username

    if email := user.email:
        current_user.email = email

    if password := user.password:
        current_user.password = get_password_hash(password)

    try:
        session.commit()
        session.refresh(current_user)

        return current_user
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Nome de usuario ou emaail já existe!",
        )


@Crud_Router.delete(
    "/Delete/{user_id}", status_code=status.HTTP_200_OK, response_model=Message
)
def delete_user(
    user_id: int,
    session: T_Session,
    current_user: CurrentUser,
):

    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você não possui permissão",
        )

    session.delete(current_user)
    session.commit()

    return Message(message="Usuario deletado!")
