from sqlalchemy import Column, Integer, String
from database.db import Base

class ConversationState(Base):
    __tablename__ = "conversation_states"

    id = Column(Integer, primary_key=True, index=True)
    step = Column(Integer, default=0)
    application_id = Column(Integer)
    session_id = Column(String, default="default")  # Add session tracking