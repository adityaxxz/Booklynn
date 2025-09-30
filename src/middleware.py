from fastapi import FastAPI
from fastapi.requests import Request
import time, logging
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

logger = logging.getLogger("uvicorn.access")
logger.disabled = True

def register_middleware(app: FastAPI):

    @app.middleware("http")
    async def custom_logging(req: Request, call_next):
        start_time = time.time()

        response = await call_next(req)
        processing_time = time.time() - start_time

        message = f"{getattr(req.client, 'host', 'unknown')}:{getattr(req.client, 'port', 'unknown')} — {req.method} — {req.url.path} — {response.status_code} completed after {processing_time}s"

        print(message)
        return response

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
        allow_credentials=True,
    )

    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["localhost", "127.0.0.1"],
    )

