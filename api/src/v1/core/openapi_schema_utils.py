# from fastapi import FastAPI
# from fastapi.openapi.utils import get_openapi


# def get_custom_openapi_schema(app: FastAPI):
#     if app.openapi_schema:
#         return app.openapi_schema
    
#     openapi_schema = get_openapi(title=app.title, version=app.version, description=app.description, routes=app.routes)
    
#     openapi_schema["components"]["securitySchemes"] = {
#         "UserApiKey": {
#             "type": "apiKey",
#             "in": "header",
#             "name": "user-api-key",
#             "description": "User API key for authenticated user operations"
#         },
#         "AdminApiKey": {
#             "type": "apiKey",
#             "in": "header",
#             "name": "admin-api-key",
#             "description": "Admin API key for administrative operations"
#         },
#         "SystemApiKey": {
#             "type": "apiKey",
#             "in": "header",
#             "name": "system-api-key",
#             "description": "System API key for internal operations"
#         }
#     }
    
#     return app.openapi_schema
