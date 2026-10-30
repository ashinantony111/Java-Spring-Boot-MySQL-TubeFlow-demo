import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from app import config
from app.database import db_manager, get_db
from app.seed_data import seed_database
from app.routes import api, db_admin, views

logger = logging.getLogger("tubeflow")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: ensure schema and seed initial data
    logger.info("Initializing TubeFlow application...")
    try:
        from app.models import Base
        if db_manager.engine:
            Base.metadata.create_all(bind=db_manager.engine)
            # Seed data
            db = db_manager.SessionLocal()
            try:
                seed_database(db)
            finally:
                db.close()
    except Exception as e:
        logger.error("Error during startup initialization: %s", e)
    yield
    logger.info("Shutting down TubeFlow application...")

app = FastAPI(
    title=config.APP_NAME,
    description=config.APP_DESCRIPTION,
    version=config.APP_VERSION,
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory=str(config.STATIC_DIR)), name="static")

# Include Routers
app.include_router(views.router)
app.include_router(api.router)
app.include_router(db_admin.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=config.APP_HOST, port=config.APP_PORT, reload=True)
