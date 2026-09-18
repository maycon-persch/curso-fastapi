from fastapi import APIRouter, status, HTTPException
from .schemas import UserCreate, UserResponse, Database, UserList, Message
from .database import database

# ───── CRUD TESTE ────────────────────────────────────────────────────────────
Crud = APIRouter(prefix="/users", tags=["Users teste do curso "])


@Crud.post(
    "/create", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
async def post_user(user: UserCreate):
    add_id_user = Database(id=len(database) + 1, **user.model_dump())
    database.append(add_id_user)
    return add_id_user


@Crud.get("/Read", response_model=UserList, status_code=status.HTTP_200_OK)
async def get_user():
    if len(database) <= 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Nenhum usuario cadastrado",
        )
    return {"users": database}


@Crud.put(
    "/Update/{user_id}",
    status_code=status.HTTP_200_OK,
    response_model=UserResponse,
)
async def update_user(user: UserCreate, user_id: int):
    add_id_user = Database(id=user_id, **user.model_dump())
    if user_id < 1 or user_id > len(database):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario não encontrado",
        )

    database[user_id - 1] = add_id_user

    return add_id_user


@Crud.delete(
    "/Delete/{user_id}", status_code=status.HTTP_200_OK, response_model=Message
)
async def delete_user(user_id: int):

    if user_id < 1 or user_id > len(database):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario não encontrado",
        )
    del database[user_id - 1]

    return {"message": "Usuario deletado com sucesso!"}
