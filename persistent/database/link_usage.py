import uuid

from sqlalchemy.sql import func
from sqlalchemy import Column, TEXT, DATETIME
from persistent.database.base import Base

def _uuid4_as_str() -> str:
    return str(uuid.uuid4())

class LinkUsage(Base):
    __tablename__ = 'linkusage'

    id = Column(TEXT, default= _uuid4_as_str, primary_key= True)


    short_link_id = Column(TEXT, nullable= False)
    user_ip = Column(TEXT, nullable= False)
    user_agent = Column(TEXT, nullable= False)

    created_at = Column(DATETIME(timezone= True), default= func.now(), nullable= False)