from collections.abc import Callable
from typing import Awaitable
from fastapi import FastAPI, HTTPException, Response, status
from httpx import Request
from pydantic import BaseModel
from services.link_service import LinkService
from utils.utils_check import link_check
from utils.utils_correction import link_correction
from fastapi.responses import JSONResponse
from loguru import logger
import time


def create_app() -> FastAPI:
    app = FastAPI()
    short_link_service = LinkService()

    class PutLink(BaseModel):
        link: str

    def _service_link_to_real(short_link: str) -> str:
        return f"http://127.0.0.1:8000/{short_link}"

    #Логгер исключений
    @app.exception_handler(Exception)
    async def catch_all(request: Request, exc: Exception):
        logger.error(f"Error in {request.method} {request.url}: {exc} \n"
                     f"Request error info: {request.headers}")
        return JSONResponse(status_code= 500, content= 'Something went wrong')

    @app.middleware('http')
    async def add_time_process_header(request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:

        start_time = time.time()

        response = await call_next(request)
        elapsed_ms = round((time.time() - start_time) * 1000, 2)
        response.headers["X-Latency"] = str(elapsed_ms) + ' ms'

        return response


    @app.post("/link")
    def create_link(put_link_request: PutLink) -> PutLink:
        if not link_check(put_link_request.link):
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail='Invalid link')

        put_link_request.link = link_correction(put_link_request.link)

        short_link = short_link_service.create_link(put_link_request.link)
        return PutLink(link=_service_link_to_real(short_link))

    @app.get("/{link}")
    def get_link(link: str) -> Response:
        real_link = short_link_service.get_real_link(link)

        if real_link is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Short link not found:(")

        return Response(status_code=status.HTTP_301_MOVED_PERMANENTLY, headers={"Location": real_link})

    return app