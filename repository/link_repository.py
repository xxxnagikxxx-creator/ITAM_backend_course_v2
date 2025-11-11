from infrastructure.database.connection import create_all_tables, pg_connection
from persistent.database.link import Link
from persistent.database.link_usage import LinkUsage
from sqlalchemy import insert, select
from sqlalchemy.orm import Mapped
from typing import Sequence
from persistent.database.link_usage import LinkUsage


class LinkRepository:
    def __init__(self) -> None:
        self._sessionmaker = pg_connection()
        create_all_tables()

    async def put_link(self, short_link: str, real_link: str) -> None:
        stmp = insert(Link).values({"short_link": short_link, "real_link": real_link})

        async with self._sessionmaker() as session:
            await session.execute(stmp)
            await session.commit()

    async def put_link_usage(self, user_agent: str, user_ip: str, short_link_id: str):
        stmp = insert(LinkUsage).values({"short_link_id": short_link_id, "user_ip": user_ip, "user_agent": user_agent})

        async with self._sessionmaker() as session:
            await session.execute(stmp)
            await session.commit()

    async def get_link(self, short_link: str) -> Link | None:
        stmp = select(Link).where(Link.short_link == short_link).limit(1)

        async with self._sessionmaker() as session:
            resp = await session.execute(stmp)

        row = resp.fetchone()
        if row is None:
            return None

        return row[0]

    async def get_link_usage(self, short_link_id: str, page: int, page_size: int) -> list[LinkUsage]:
        offset = max(page - 1, 0) * page_size
        stmp = select(LinkUsage).where(LinkUsage.short_link_id == short_link_id).order_by(LinkUsage.created_at.desc()).offset(offset).limit(page_size)

        async with self._sessionmaker() as session:
            resp = await session.execute(stmp)

        return [row[0] for row in resp.fetchall()]