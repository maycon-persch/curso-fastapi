from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.models import User
from app.schemas import (
    Token,
)
from app.security import (
    create_access_token,
    get_current_user,
    verify_password,
)

Auth_Router = APIRouter(prefix="/token", tags=["Autenticação de usuario"])

OAuthForm = Annotated[OAuth2PasswordRequestForm, Depends()]
T_Session = Annotated[AsyncSession, Depends(get_session)]


@Auth_Router.post("/post-token/", response_model=Token)
async def login_for_access_token(
    form_data: OAuthForm,
    session: T_Session,
):
    user_db = await session.scalar(
        select(User).where(User.email == form_data.username)
    )
    if not user_db:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Login inválido!",
        )

    print("usuario encontrado")

    if not verify_password(
        form_data.password, user_db.password
        ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Login inválido!",
        )

    print("senha confirmada")

    access_token = create_access_token(
        data={"sub": user_db.email}
        )

    return {"access_token": access_token, "token_type": "Bearer"}


@Auth_Router.post("/refresh-token/", response_model=Token)
async def refresh_access_token(
    user: Annotated[User, Depends(get_current_user)]
):
    new_access_token = create_access_token(
        data={"sub": user.email}
    )
    return {"access_token": new_access_token, "token_type": "Bearer"}
