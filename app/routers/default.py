from fastapi import APIRouter

from app.schemas import Message

Default_Router = APIRouter(tags=["Rotas Defaults"])


@Default_Router.get("/", response_model=Message)
def get_bem_vindo():
    return Message(message="Bem vindo a minha API do curso do Eduardo Mendes!")
