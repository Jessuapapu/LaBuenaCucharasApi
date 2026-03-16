from fastapi import FastAPI
from .routes.main_router import app_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.include_router(app_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



print(f"La app inicio correctamente, la url base es http://localhost:8000")
