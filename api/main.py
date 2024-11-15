from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from shared.core.error_handlers import api_error_handler
from shared.core.exceptions import APIException
from shared.settings import get_settings
from shared.database import Database
from api.routers import canteen_router, menu_router, dish_router, taste_router, user_router



def create_app():
    load_dotenv()
    settings = get_settings()
    eat_prefix = settings.BASE_PREFIX_EAT
    
    app = FastAPI(title="lmu-dev-api", description="API for Students App in Munich.", version="0.1.0", docs_url="/docs", contact={"name": "LMU Developers", "email": "contact@lmu-dev.org"})
    
    # Add exception handlers
    app.add_exception_handler(Exception, api_error_handler)
    app.add_exception_handler(APIException, api_error_handler)
    
    # Add static files
    app.mount(path=f"{eat_prefix}/images", app= StaticFiles(directory="/app/shared/images/canteens"), name="images")
    
    # Include routers
    app.include_router(canteen_router.router,   prefix=eat_prefix, tags=["canteen"])
    app.include_router(menu_router.router,      prefix=eat_prefix, tags=["canteen"])
    app.include_router(dish_router.router,      prefix=eat_prefix, tags=["canteen"])
    app.include_router(taste_router.router,     prefix=eat_prefix, tags=["canteen"])
    app.include_router(user_router.router,      prefix=eat_prefix, tags=["user"])
    
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
    Database(settings=settings)

    return app


def main():
    print("Running main()...")
    return create_app()

app = main()  # This line is crucial, gets called in Dockerfile
