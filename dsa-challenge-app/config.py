import os
import sys

# Base directory
if getattr(sys, 'frozen', False):
    BASE_DIR = sys._MEIPASS
    DATA_DIR = os.path.join(os.path.dirname(sys.executable), 'data')
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DATA_DIR = os.path.join(BASE_DIR, 'data')

# Database configuration
# Use DATABASE_URL if provided (e.g. by Render/Heroku), otherwise use local SQLite
DB_PATH = os.path.join(DATA_DIR, 'contest_v2.db')
DATABASE_URL = os.environ.get('DATABASE_URL')
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    # SQLAlchemy 1.4+ deprecated postgres://, needs postgresql://
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

SQLALCHEMY_DATABASE_URI = DATABASE_URL if DATABASE_URL else f'sqlite:///{DB_PATH}'

# Problem configuration
PROBLEMS_DIR = os.path.join(DATA_DIR, 'problems')
TOTAL_PROBLEMS = 10

# Execution configuration
EXECUTION_TIMEOUT = 10  # seconds (Safe for high concurrency)
TEMP_DIR = os.path.join(DATA_DIR, 'temp')

# Contest configuration
CONTEST_DURATION = 7200  # 2 hours in seconds

# Scoring configuration
MARKS_PER_PROBLEM = 10
TOTAL_MARKS = TOTAL_PROBLEMS * MARKS_PER_PROBLEM

# Performance levels - Relative ranking based on percentile
GOLD_PERCENTILE = 30    # Top 30% get Gold
SILVER_PERCENTILE = 70  # Next 40% (30-70%) get Silver
# Bottom 30% (70-100%) get Bronze

def get_performance_level(rank, total_participants):
    """
    Calculate performance level based on relative ranking
    rank: participant's rank (1 = best)
    total_participants: total number of participants
    """
    if total_participants == 0:
        return "Participant"
    
    percentile = (rank / total_participants) * 100
    
    if percentile <= GOLD_PERCENTILE:
        return "Gold"
    elif percentile <= SILVER_PERCENTILE:
        return "Silver"
    else:
        return "Bronze"

# Ensure directories exist
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(PROBLEMS_DIR, exist_ok=True)
os.makedirs(TEMP_DIR, exist_ok=True)
