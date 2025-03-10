import sys
import yaml
from fastapi import FastAPI, Request
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html
from fastapi.responses import Response
from fastapi.openapi.utils import get_openapi
from fastapi.middleware.cors import CORSMiddleware
from sentry_sdk.integrations.asgi import SentryAsgiMiddleware
from src import router_pharma, router_auth
# from src.connection.cognito import get_current_user
from dotenv import load_dotenv
from src.engine.font import register_font_family, cambria_fonts

load_dotenv()

sys.setrecursionlimit(sys.getrecursionlimit() * 5)

app = FastAPI(  
    title="Pharma API",
    version="2.5.0",
    description="This is the Pharma API for the Pharma project",
    openapi_url="/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    # dependencies=[Depends(get_current_user)]
)

AllOWED_ORIGINS = [
    "*",
    "http://localhost:3000",
    "http://localhost:8000",
]

# CORS Middleware with AWS Cognito support
app.add_middleware(
    CORSMiddleware, 
    allow_origins = AllOWED_ORIGINS,
    allow_credentials = True,
    allow_methods = ["*"],
    allow_headers = ["*"],
)

# Add Sentry Middleware
app.add_middleware(SentryAsgiMiddleware)

# Include the router for pharma-related endpoints and secure endpoints with aws cognito
# app.include_router(router_pharma.get_router(), prefix="/elixir", dependencies = [Depends(get_current_user)])
app.include_router(router_auth.get_router(), prefix="/auth", tags=["Pharma Auth"])
app.include_router(router_pharma.get_router(), prefix="/elixir", tags=["Pharma"])

@app.on_event("startup")
async def font():
    # Register the Cambria font family
    return register_font_family("Cambria", cambria_fonts)

# # Secure routes
# @app.get("/secure-data")
# async def get_secure_data(current_user: Dict = Depends(get_current_user)):
#     return {"message": "This is secure data", "user": current_user}

# Debugging route to trigger Sentry errors
@app.get("/sentry-debug")
async def trigger_error():
    raise ValueError("This is a test error")

# Root endpoint with YAML response
@app.get("/", response_class=Response)
async def read_root(request: Request):
    response_data = {"Mesaage": "Hello World!, Welcome to Pharma Api"}
    return Response(
        content=yaml.dump(response_data), 
        media_type="application/x-yaml",
        headers={
            "Access-Control-Allow-Origin": "*", 
            "Access-Control-Allow-Headers": "Origin, X-Requested-With, Content-Type, Accept"
        }
    )


# Custom Swagger UI documentation
@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title="Pharma API"
    )


# Custom ReDoc documentation
@app.get("/redoc", include_in_schema=False)
async def redoc_html():
    return get_redoc_html(
        openapi_url="/openapi.yaml",
        title="Pharma API"
    )

# OpenAPI schema in YAML format
@app.get("/openapi.yaml", include_in_schema=False, response_class=Response)
async def custom_openapi():
    openapi_schema = get_openapi(
        title="Pharma", 
        version="2.5.0", 
        routes=app.routes
    )
    return Response(
        content=yaml.dump(openapi_schema), 
        media_type="application/x-yaml"
    )

# Run the FastAPI application using Uvicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
