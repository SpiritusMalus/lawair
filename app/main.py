from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.core.search import ensure_index, make_client
from app.routers import auth, deals, lawyers, profile, services, users


@asynccontextmanager
async def lifespan(app: FastAPI):
    es = make_client()
    await ensure_index(es)
    await es.close()
    yield


app = FastAPI(title=settings.PROJECT_NAME, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(profile.router)
app.include_router(services.router)
app.include_router(lawyers.router)
app.include_router(deals.router)
