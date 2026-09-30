from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.models import User
from app.schemas import (
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

T_Session = Annotated[AsyncSession, Depends(get_session)]
CurrentUser = Annotated[User, Depends(get_current_user)]


@Crud_Router.post(
    "/create", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
async def post_user(user: UserCreate, session: T_Session):

    db_user = await session.scalar(
        select(User).where(
            (User.email == user.email)
        )
    )
    if db_user:
        if db_user.email == user.email:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Esse E-mail ja está em uso!",
            )

    db_user = User(
        name=user.name,
        email=user.email,
        password=get_password_hash(user.password),
    )
    session.add(db_user)
    await session.commit()
    await session.refresh(db_user)

    return db_user


@Crud_Router.get("/get/id", status_code=status.HTTP_200_OK)
async def get_id(
    current_user: CurrentUser,
):
    return {"id": current_user.id}


@Crud_Router.get(
    "/Read", response_model=UserList, status_code=status.HTTP_200_OK
)
async def get_user(
    session: T_Session,
    current_user: CurrentUser,
    pagina: Annotated[int, Query(ge=1, )] = 1
):
    users = await session.scalars(
        select(User).limit(10).offset((pagina * 10) - 10))
    return {"users": users}


@Crud_Router.put(
    "/Update/{user_id}",
    status_code=status.HTTP_200_OK,
    response_model=UserResponse,
)
async def update_user(
    user: UserPut,
    user_id: int,
    session: T_Session,
    current_user: CurrentUser,
):

    if not current_user.is_admin:
        if current_user.id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Você não possui permissão",
            )

        if name := user.name:
            current_user.name = name

        if email := user.email:
            current_user.email = email

        if password := user.password:
            current_user.password = get_password_hash(password)

        try:
            await session.commit()
            await session.refresh(current_user)

            return current_user
        except IntegrityError:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Este E-mail já existe!",
            )

    else:
        user_db = await session.scalar(select(User).where(User.id == user_id))

        if not user_db:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario não encontrado",
            )
        if name := user.name:
            user_db.name = name

        if email := user.email:
            user_db.email = email

        if password := user.password:
            user_db.password = get_password_hash(password)

        try:
            await session.commit()
            await session.refresh(user_db)

            return user_db
        except IntegrityError:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Este email já existe!",
            )


@Crud_Router.delete(
    "/delete/{user_id}", status_code=status.HTTP_200_OK, response_model=Message
)
async def delete_user(
    user_id: int,
    session: T_Session,
    current_user: CurrentUser,
):
    if not current_user.is_admin:
        raise HTTPException(
            detail='Voce num pode ♥', status_code=status.HTTP_403_FORBIDDEN
            )

    user = await session.scalar(select(User).where(User.id == user_id))

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario não encontrado!"
        )

    await session.delete(user)
    await session.commit()

    return Message(message="Usuario deletado!")
