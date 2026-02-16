from sqlalchemy import Column, String
from ..db import Base


class User(Base):
    __tablename__ = "users"

    user_id = Column(String(10), primary_key=True)
    name = Column(String(100), nullable=False)
    city = Column(String(100))
    segment = Column(String(50))
