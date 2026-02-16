from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from ..db import Base


class Notification(Base):
    __tablename__ = "notifications"

    notification_id = Column(String(50), primary_key=True)
    user_id = Column(String(10), ForeignKey("users.user_id"), nullable=False)
    channel = Column(String(50))
    message = Column(Text)
    sent_at = Column(DateTime)

    user = relationship("User")
