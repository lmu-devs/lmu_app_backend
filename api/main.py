from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from shared.core.exceptions import APIException
from shared.database import Database
from shared.core.error_handlers import api_error_handler
from shared.settings import get_settings
from shared.core.logging import get_api_logger
from api.routers import canteen_router, feedback_router, log_router, menu_router, dish_router, taste_router, user_router, wishlist_router

api_logger = get_api_logger(__name__)


def create_app():
    settings = get_settings()
    eat_prefix = settings.BASE_PREFIX_EAT
    
    app = FastAPI(
        title="lmu-dev-api", 
        description="API for Students App in Munich.", 
        version="0.1.1", 
        docs_url="/docs", 
        contact={"name": "LMU Developers", "email": "contact@lmu-dev.org"},
    )
    
    # Add exception handlers
    app.add_exception_handler(Exception, api_error_handler)
    app.add_exception_handler(APIException, api_error_handler)
    
    # Add static files
    app.mount(path=f"{eat_prefix}/images", app= StaticFiles(directory="/app/shared/assets/canteens"), name="images")
    
    # Include routers
    app.include_router(canteen_router.router,   prefix=eat_prefix, tags=["canteen"])
    app.include_router(menu_router.router,      prefix=eat_prefix, tags=["canteen"])
    app.include_router(dish_router.router,      prefix=eat_prefix, tags=["canteen"])
    app.include_router(taste_router.router,     prefix=eat_prefix, tags=["canteen"])
    app.include_router(user_router.router,                         tags=["user"])
    app.include_router(log_router.router,                          tags=["log"])
    app.include_router(feedback_router.router,                     tags=["feedback"])
    app.include_router(wishlist_router.router,                     tags=["wishlist"])
    
    # Add middleware to allow CORS (Cross-Origin Resource Sharing)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["https://students-app.lmu-dev.org","http://localhost:53480"],
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE"],
        allow_headers=["*"],
    )
    
    # Middleware to add charset to JSON responses for üäö
    @app.middleware("http")
    async def add_charset_middleware(request: Request, call_next):
        response = await call_next(request)
        if response.headers.get("content-type") == "application/json":
            response.headers["content-type"] = "application/json; charset=utf-8"
        return response

    @app.get("/", include_in_schema=False)
    async def root():
        return {"message": "Hello Wörld"}
    
    # Initialize the database
    try:
        Database(settings=settings)
    except Exception as e:
        api_logger.fatal(f"Error initializing database: {e}")
        raise APIException(f"Error initializing database: {e}")

    return app


def main():
    api_logger.info("Running main()")
    return create_app()

app = main()  # This line is crucial, gets called in Dockerfile
