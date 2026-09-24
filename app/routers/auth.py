from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_session
from app.models import User
from app.schemas import (
    Token,
)
from app.security import (
    create_access_token,
    verify_password,
)

Auth_Router = APIRouter(tags=["Autenticação de usuario"])

OAuthForm = Annotated[OAuth2PasswordRequestForm, Depends()]
T_Session = Annotated[Session, Depends(get_session)]


@Auth_Router.post("/token/get-token/", response_model=Token)
def login_for_access_token(
    form_data: OAuthForm,
    session: T_Session,
):
    user_db = session.scalar(
        select(User).where(User.email == form_data.username)
    )

    if not user_db:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Login inválido!",
        )

    print("usuario encontrado")

    if not verify_password(form_data.password, user_db.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Login inválido!",
        )

    print("senha confirmada")

    access_token = create_access_token(data={"sub": user_db.email})

    return {"access_token": access_token, "token_type": "Bearer"}
