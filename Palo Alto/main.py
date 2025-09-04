# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routers import auth as auth_router
from api.routers import users as users_router
from api.routers import entries as entries_router
from api.routers import insights as insights_router
from api.routers import ai as ai_router


app = FastAPI()
app.include_router(ai_router.router)
# --- CORS: allow your Vite dev server ---
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,  # okay even if you don't use cookies
    allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# --- Mount routers with the prefixes your frontend uses ---
app.include_router(auth_router.router, prefix="/auth", tags=["auth"])
app.include_router(users_router.router, prefix="/users", tags=["users"])
app.include_router(entries_router.router, prefix="/entries", tags=["entries"])
app.include_router(insights_router.router, prefix="/insights", tags=["insights"])
