from fastapi import FastAPI
from .routes.main_router import app_router

app = FastAPI()
app.include_router(app_router)

print(f"La app inicio correctamente, la url base es http://localhost:8000")
