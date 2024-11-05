# Path: ai_agent_project/src/db/models.py

from sqlalchemy import Column, Integer, String, ForeignKey, Text, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Agent(Base):
    __tablename__ = 'agents'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    # Add other relevant fields

    tasks = relationship("Task", back_populates="agent")


class Task(Base):
    __tablename__ = 'tasks'

    id = Column(Integer, primary_key=True, index=True)
    description = Column(Text, nullable=False)
    agent_id = Column(Integer, ForeignKey('agents.id'))
    priority = Column(Integer, default=1)
    use_chain_of_thought = Column(Boolean, default=False)
    status = Column(String, default="queued")  # e.g., queued, running, completed, failed
    result = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    agent = relationship("Agent", back_populates="tasks")
