from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from api.v1.feedback.routers import feedback_router
from api.v1.food.routers import (canteen_router, dish_router, menu_router,
                                 taste_router)
from api.v1.log.routers import log_router
from api.v1.movie.routers import movie_router
from api.v1.user.routers import user_router
from api.v1.wishlist.routers import wishlist_router
from shared.core.error_handlers import api_error_handler
from shared.core.exceptions import APIException
from shared.core.logging import get_food_api_logger
from shared.database import Database
from shared.settings import get_settings

api_logger = get_food_api_logger(__name__)


def create_app():
    settings = get_settings()
    prefix = settings.API_V1_BASE_PREFIX
    eat_prefix = settings.API_V1_BASE_PREFIX_FOOD
    
    app = FastAPI(
        title="lmu-dev-api", 
        description="API for Students App in Munich.", 
        version="1.1.5", 
        docs_url=f"{prefix}/docs", 
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
    app.include_router(user_router.router,      prefix=prefix, tags=["user"])
    app.include_router(log_router.router,       prefix=prefix, tags=["log"])
    app.include_router(feedback_router.router,  prefix=prefix, tags=["feedback"])
    app.include_router(wishlist_router.router,  prefix=prefix, tags=["wishlist"])
    app.include_router(movie_router.router,     prefix=prefix, tags=["movie"])
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
