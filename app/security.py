from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from pwdlib import PasswordHash
from jwt import encode, decode, DecodeError
from fastapi import Depends, HTTPException, status
from app.database import get_session
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token/get-token/")

SECRET_KEY = "your-secret-key-and-exclusive-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = PasswordHash.recommended()


def create_access_token(data: dict):

    to_encode = data.copy()

    expire = datetime.now(tz=ZoneInfo("UTC")) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )
    to_encode.update({"exp": expire})

    encoded_jwt = encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt


def get_password_hash(password: str):

    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)


def get_current_user(
    session: Session = Depends(get_session),
    token: str = Depends(oauth2_scheme),
):

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciais invalidas!",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        subject_email = payload.get("sub")

        if not subject_email:
            raise credentials_exception
    except DecodeError:
        raise credentials_exception

    user_db = session.scalar(select(User).where(User.email == subject_email))

    if not user_db:
        raise credentials_exception

    return user_db
