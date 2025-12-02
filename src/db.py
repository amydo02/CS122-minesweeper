import os
from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Float,
    ForeignKey,
    UniqueConstraint,
)
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

# path up dir to get to main project root
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(PROJECT_ROOT, "minesweeper.db")

engine = create_engine(f"sqlite:///{DB_PATH}", echo=False, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

Base = declarative_base()

#User Table
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    normalized_name = Column(String, nullable=False, unique=True)
    pin = Column(String, nullable=False)

    stats = relationship(
        'UserDifficultyStat',
        back_populates='user',
        cascade='all, delete-orphan',
    )
#Stats Table
class UserDifficultyStat(Base):
    __tablename__ = 'user_difficulty_stats'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    difficulty = Column(String, nullable=False)
    best_time = Column(Float, nullable=True)
    best_score = Column(Integer, nullable=True)

    user = relationship('User', back_populates='stats')

    #only allow each combination of user id and diff to exist once
    __table_args__ = (
        UniqueConstraint('user_id', 'difficulty', name='uix_user_diff'),
    )

def init_db():
    Base.metadata.create_all(engine)
