from collections.abc import Callable
from typing import Awaitable
from fastapi import FastAPI, HTTPException, Response, status, Request
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



    def _service_link_to_real(short_link: str, request: Request) -> str:
        hostname = request.url.hostname
        port = request.url.port or 8000
        scheme = request.url.scheme
        return f"{scheme}://{hostname}:{port}/{short_link}"

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
    async def create_link(put_link_request: PutLink, request: Request) -> PutLink:
        if not link_check(put_link_request.link):
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail='Invalid link')

        put_link_request.link = link_correction(put_link_request.link)

        short_link = await short_link_service.create_link(put_link_request.link)
        return PutLink(link=_service_link_to_real(short_link, request))

    @app.get("/{link}")
    async def get_link(link: str, request: Request) -> Response:
        real_link = await short_link_service.get_real_link(link)

        if real_link is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Short link is not found:(")

        user_agent = request.headers.get('user-agent', '')
        user_ip = request.client.host if request.client else ''
        await short_link_service.put_link_usage(short_link=link, user_ip=user_ip, user_agent=user_agent)

        return Response(
            status_code=status.HTTP_307_TEMPORARY_REDIRECT,
            headers={
                "Location": real_link,
                "Cache-Control": "no-store, no-cache, must-revalidate, max-age=0",
                "Pragma": "no-cache",
                "Expires": "0",
            },
        )

    @app.get("/{short_link}/statistics")
    async def get_usage_statistics(short_link: str, page: int, page_size: int) -> Response:

        if short_link is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Short link is not found:(")

        usage_statistics = await short_link_service.get_usage_statistics(short_link, page, page_size)

        if usage_statistics is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No short link statistics:(")

        return usage_statistics





    return app
