from fastapi import APIRouter, status, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from app.schemas import (
    UserCreate,
    UserResponse,
    UserList,
    Message,
    UserPut,
    Token,
)
from .database import get_session
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    get_current_user,
)
from app.models import User

# ───── CRUD TESTE ────────────────────────────────────────────────────────────
Crud_Router = APIRouter(prefix="/users", tags=["Users teste do curso "])

Token_Router = APIRouter(tags=["Autenticação de usuario"])


@Crud_Router.post(
    "/create", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
def post_user(user: UserCreate, session: Session = Depends(get_session)):

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
    current_user: User = Depends(get_current_user),
):
    return {"id": current_user.id}


@Crud_Router.get(
    "/Read", response_model=UserList, status_code=status.HTTP_200_OK
)
def get_user(
    pagina: int = 0,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
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
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):

    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você não possui permissão",
        )

    try:
        if username := user.username:
            current_user.username = username

        if email := user.email:
            current_user.email = email

        if password := user.password:
            current_user.password = get_password_hash(password)

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
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):

    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você não possui permissão",
        )

    session.delete(current_user)
    session.commit()

    return Message(message="Usuario deletado!")


@Token_Router.post("/token/get-token/", response_model=Token)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session),
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
