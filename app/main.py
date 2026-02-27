from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.auth.router import router as auth_router
from app.users.router import router as users_router
from app.group.router import router as group_router
from app.memory.router import router as memory_router
from app.recall.router import router as recall_router
from app.comment.router import router as comment_router
from app.upload.router import router as upload_router
from app.core.config import settings

app = FastAPI(
    title="마씨(Merci) API",
    version="0.1.0",
    docs_url="/docs" if settings.SHOW_DOCS else None,
    redoc_url="/redoc" if settings.SHOW_DOCS else None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router,    prefix="/auth",    tags=["auth"])
app.include_router(users_router,   prefix="/users",   tags=["users"])
app.include_router(group_router,   prefix="/groups",  tags=["groups"])
app.include_router(memory_router,  prefix="/memories", tags=["memories"])
app.include_router(recall_router,  prefix="/memories", tags=["recalls"])
app.include_router(comment_router, prefix="/memories", tags=["comments"])
app.include_router(upload_router,  prefix="/uploads", tags=["uploads"])


@app.get("/health", tags=["health"])
async def health_check():
    return {"status": "ok"}
