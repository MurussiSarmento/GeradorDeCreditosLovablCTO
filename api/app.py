from fastapi import FastAPI
from utils.logger import init_logger
from core.config import load_env, Settings
from api.routers.health import router as health_router
from api.routers.emails import router as emails_router
from api.routers.messages import router as messages_router
from api.routers.auth import router as auth_router
from api.routers.jobs import router as jobs_router
from api.routers.webhooks import router as webhooks_router
from api.routers.codes import router as codes_router
from api.rate_limit import RateLimiterMiddleware
from core.mail_tm.client import MailTmClient


def create_app() -> FastAPI:
    load_env()
    settings = Settings()
    logger = init_logger(level=settings.LOG_LEVEL)

    app = FastAPI(title="Mail.tm API", version="0.1.0")
    app.state.settings = settings
    app.state.logger = logger
    app.state.mail_client = MailTmClient()
    # Registry de jobs simples na memória
    import threading
    app.state.jobs = {}
    app.state.jobs_lock = threading.Lock()
    # Garantir que o banco e tabelas existem
    try:
        from core.database.session import get_engine
        from core.database.models import Base
        engine = get_engine()
        Base.metadata.create_all(engine)
    except Exception:
        pass

    app.include_router(health_router)
    app.include_router(auth_router)
    app.include_router(emails_router)
    app.include_router(messages_router)
    app.include_router(jobs_router)
    app.include_router(webhooks_router)
    app.include_router(codes_router)
    app.add_middleware(RateLimiterMiddleware)
    return app


app = create_app()