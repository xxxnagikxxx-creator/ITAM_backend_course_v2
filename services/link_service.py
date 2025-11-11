from utils.utils_random import random_alfanum
from repository.link_repository import LinkRepository
from typing import Any

class LinkService:
    def __init__(self) -> None:
        self._link_repository = LinkRepository()

    async def create_link(self, real_link: str) -> str:
        short_link = random_alfanum(5)
        await self._link_repository.put_link(short_link, real_link)
        return short_link

    async def get_real_link(self, short_link: str) -> str | None:
        link = await self._link_repository.get_link(short_link= short_link)
        if link is None:
            return None

        return str(link.real_link)

    async def put_link_usage(self, short_link: str, user_ip: str, user_agent: str) -> None:
        link = await self._link_repository.get_link(short_link= short_link)
        if link is None:
            return None
        await self._link_repository.put_link_usage(user_agent=user_agent, user_ip=user_ip, short_link_id=str(link.id))

    async def get_usage_statistics(self, short_link: str, page: int, page_size: int) -> list[dict[str, Any]] | None:
        link = await self._link_repository.get_link(short_link= short_link)
        if link is None:
            return None

        rows = await self._link_repository.get_link_usage(short_link_id=str(link.id), page=page, page_size=page_size)

        result: list[dict[str, Any]]= []
        for item in rows:
            result.append({"user_ip": item.user_ip,
                           "user_agent": item.user_agent,
                           "created_at": str(item.created_at)})
        return result