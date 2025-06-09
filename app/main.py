import logging
import sys
from typing import Union
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from fastapi.requests import Request
from fastapi.responses import FileResponse

import settings
from tools import sign_pdf
from .dto import PDFPayload


logger = logging.getLogger('uvicorn.error')
if settings.DEBUG:
    logger.setLevel(logging.DEBUG)
else:
    logger.setLevel(logging.INFO)

# Check python version
if not sys.version_info[0:2] >= settings.REQUIRED_PYTHON:
    sys.exit(f"Python {settings.REQUIRED_PYTHON} required.")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.debug(
        f" ***** Service PDF-SIGNET {settings.VERSION} has started ***** "
    )
    yield
    logger.debug(" ***** Service PDF-SIGNET shutting down (cleanly) ***** ")
    app.user_middleware.clear()
    app.middleware_stack = app.build_middleware_stack()
    logger.debug(" ***** Shutdown procedure: Middleware deactivated ***** ")


app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
app.add_middleware(HTTPSRedirectMiddleware)
app.add_middleware(
    TrustedHostMiddleware, allowed_hosts=settings.AUTHORIZED_HOSTS
)
app.add_middleware(GZipMiddleware, minimum_size=1000)


@app.post("/sign_document")
async def sign_pdf_document(data: PDFPayload) -> bytes:
    try:
        signed_pdf = sign_pdf(data)
    except Exception as e:
        logger.error(f"Error signing PDF: {e}")
        return {"status": "error", "message": str(e)}   
    return FileResponse(signed_pdf, media_type="application/pdf")

@app.api_route("/{path_name:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def catch_all(request: Request, path_name: str):
    return {"status": "error", "message": "Operation not permitted"}