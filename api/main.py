from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from shared.core.error_handlers import api_error_handler
from shared.core.exceptions import APIException
from shared.settings import get_settings
from shared.database import Database
from api.routers import canteen_router, menu_router, dish_router, taste_router, user_router



def create_app():
    load_dotenv()
    app = FastAPI(title="lmu-eat-api", description="API for canteen and menu data from munich.", version="0.1.0")
    
    # Add exception handlers
    app.add_exception_handler(Exception, api_error_handler)
    app.add_exception_handler(APIException, api_error_handler)
    
    # Include routers
    app.include_router(canteen_router.router,   prefix="/eat/v1", tags=["canteen"])
    app.include_router(menu_router.router,      prefix="/eat/v1", tags=["menu"])
    app.include_router(dish_router.router,      prefix="/eat/v1", tags=["dish"])
    app.include_router(user_router.router,      prefix="/eat/v1", tags=["user"])
    app.include_router(taste_router.router,     prefix="/eat/v1", tags=["taste"])
    
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

    @app.get("/")
    async def root():
        return {"message": "Hello Wörld"}
    
    # Initialize the database
    settings = get_settings()
    Database(settings=settings)

    return app


def main():
    print("Running main()...")
    return create_app()

app = main()  # This line is crucial, gets called in Dockerfile
