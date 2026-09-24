from fastapi import FastAPI

from app.routers.auth import Auth_Router
from app.routers.default import Default_Router
from app.routers.users import Crud_Router

app = FastAPI(
    title="Curso de API",
    description="Curso de FastAPI com Eduardo Mendes no You Tube"
    "de como criar uma API do zero",
    version="6.7",
)


app.include_router(Default_Router)
app.include_router(Crud_Router)
app.include_router(Auth_Router)
