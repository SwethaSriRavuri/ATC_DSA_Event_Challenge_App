from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import config

Base = declarative_base()

class Participant(Base):
    __tablename__ = 'participants'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100))
    language = Column(String(20), nullable=False)  # 'python' or 'java'
    created_at = Column(DateTime, default=datetime.now)

class Problem(Base):
    __tablename__ = 'problems'
    
    id = Column(Integer, primary_key=True)
    problem_id = Column(Integer, unique=True, nullable=False)
    title = Column(String(200), nullable=False)
    difficulty = Column(String(20))
    marks = Column(Integer, default=10)

class Submission(Base):
    __tablename__ = 'submissions'
    
    id = Column(Integer, primary_key=True)
    participant_id = Column(Integer, nullable=False)
    problem_id = Column(Integer, nullable=False)
    code = Column(Text, nullable=False)
    language = Column(String(20), nullable=False)
    verdict = Column(String(50))  # Accepted, Wrong Answer, etc.
    score = Column(Integer, default=0)
    execution_time = Column(Float)  # in seconds
    submitted_at = Column(DateTime, default=datetime.now)

class Contest(Base):
    __tablename__ = 'contest'
    
    id = Column(Integer, primary_key=True)
    participant_id = Column(Integer, unique=True, nullable=False)
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    duration = Column(Integer)  # in seconds
    is_active = Column(Integer, default=1)  # 1 for active, 0 for ended
    status = Column(String(20), default='ACTIVE')  # ACTIVE, COMPLETED, DISQUALIFIED
    violation_count = Column(Integer, default=0)

class Result(Base):
    __tablename__ = 'results'
    
    id = Column(Integer, primary_key=True)
    participant_id = Column(Integer, unique=True, nullable=False)
    total_score = Column(Integer, default=0)
    problems_solved = Column(Integer, default=0)
    performance_level = Column(String(20))  # Gold, Silver, Bronze
    created_at = Column(DateTime, default=datetime.now)

# Database initialization
# config.SQLALCHEMY_DATABASE_URI handles both SQLite and Postgres
engine_args = {}
if 'postgresql' in config.SQLALCHEMY_DATABASE_URI:
    engine_args = {
        'pool_size': 10,
        'max_overflow': 20,
        'pool_timeout': 30,
        'pool_recycle': 1800
    }

engine = create_engine(config.SQLALCHEMY_DATABASE_URI, echo=False, **engine_args)
SessionLocal = sessionmaker(bind=engine)

def init_db():
    """Initialize database and create all tables"""
    Base.metadata.create_all(engine)
    print(f"Database initialized at {config.DB_PATH}")

def get_session():
    """Get a new database session"""
    return SessionLocal()
