import uvicorn

from backend_fastapi.fastapi_service import app
from backend_fastapi.fastapi_service.settings.settings import settings

uvicorn.run(app, host=settings.api.host, port=int(settings.api.port))
