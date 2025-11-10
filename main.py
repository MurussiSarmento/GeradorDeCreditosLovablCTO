from pathlib import Path
import uvicorn
from utils.logger import init_logger
from core.config import Settings, load_env


def main() -> None:
    # Ensure directories exist
    Path("logs").mkdir(parents=True, exist_ok=True)
    Path("data").mkdir(parents=True, exist_ok=True)

    load_env()
    settings = Settings()
    logger = init_logger(level=settings.LOG_LEVEL)

    logger.info(
        "Aplicação iniciada",
        extra={
            "api_host": settings.API_HOST,
            "api_port": settings.API_PORT,
            "database": settings.DATABASE_URL,
        },
    )

    # Initialize database
    try:
        from core.database.models import Base
        from core.database.session import get_engine
        engine = get_engine()
        Base.metadata.create_all(engine)
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")

    # Start FastAPI server
    uvicorn.run(
        "api.app:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=False,
        log_level=settings.LOG_LEVEL.lower(),
    )


if __name__ == "__main__":
    main()