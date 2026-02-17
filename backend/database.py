from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Database URL for SQLite.
SQLALCHEMY_DATABASE_URL = "sqlite:///./backend/users.db"

# Create the SQLAlchemy engine to interact with the database
# connect_args={"check_same_thread": False} is required for SQLite to allow multiple threads to access the database.
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# Create a session factory for managing database sessions
# autocommit=False: We manually commit changes
# autoflush=False: We manually flush changes to the DB
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for our database models to inherit from
Base = declarative_base()
