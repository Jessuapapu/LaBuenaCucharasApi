from fastapi import FastAPI
from .routes.main_router import router

app = FastAPI()
app.include_router(router)
