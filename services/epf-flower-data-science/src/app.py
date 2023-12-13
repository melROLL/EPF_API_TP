from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from src.api.router import router
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from fastapi.openapi.models import APIBase
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html
from fastapi.responses import HTMLResponse
from fastapi.responses import HTMLResponse, JSONResponse
from src.api.router import router


def get_application() -> FastAPI:
    application = FastAPI(
        title="epf-flower-data-science",
        description="""Fast API""",
        version="1.0.0",
        redoc_url=None,
    )

    application.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    application.include_router(router)

    # Redirect root endpoint to Swagger UI
    @application.get("/", include_in_schema=False)
    async def custom_swagger_ui_html():
        return HTMLResponse(get_swagger_ui_html(openapi_url="/openapi.json", title="Docs"))

    # OpenAPI JSON endpoint
    @application.get("/openapi.json", include_in_schema=False)
    async def get_open_api_endpoint():
        return JSONResponse(content=application.openapi(), media_type="application/json")

    return application
