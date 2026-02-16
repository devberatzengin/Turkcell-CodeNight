from sqlalchemy import Column, String
from ..db import Base


class Game(Base):
    __tablename__ = "games"

    game_id = Column(String(10), primary_key=True)
    game_name = Column(String(100), nullable=False)
    genre = Column(String(50))
