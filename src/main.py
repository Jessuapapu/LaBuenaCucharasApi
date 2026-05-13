from fastapi import FastAPI
from .routes.main_router import app_router
from fastapi.middleware.cors import CORSMiddleware

from PA import main as PA
from .models.comedor import models as comedor

from .config import socket
import socketio

from .events import *

app = FastAPI()
PA.main()
comedor.MonitorComedor()
app.include_router(app_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app = socketio.ASGIApp(socket.sio, app)
print(f"La app inicio correctamente, la url base es http://localhost:8001")
