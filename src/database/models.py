from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

# Create base class for declarative models
Base = declarative_base()

class FileMetadata(Base):
    __tablename__ = 'file_metadata'

    id = Column(Integer, primary_key=True)
    file_path = Column(String, unique=True)
    project_number = Column(String)
    department = Column(String)
    revision = Column(String)
    type = Column(String)
    area = Column(String)
    progress = Column(String)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Create database engine and session
db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'metadata.db')
engine = create_engine(f'sqlite:///{db_path}')
SessionLocal = sessionmaker(bind=engine)

# Create all tables
def init_db():
    Base.metadata.create_all(engine)