from fastapi import FastAPI
from .routers import Crud

app = FastAPI(
    title="Curso de API",
    description="Curso de FastAPI com Eduardo Mendes no You Tube de como criar uma API do zero",
    version="1.0.0",
)

app.include_router(Crud)
