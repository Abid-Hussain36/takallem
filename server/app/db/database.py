"""
Database Configuration Module

This module sets up the SQLAlchemy engine and session for connecting to Supabase PostgreSQL database.
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL env variable is not set")

# Engine manages connections to the database
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # Ensures connection is alive before using it
    echo=False  # Set to True to see SQL queries in console
)

# A Session is what you use to talk to the database.
# SessionLocal is a factory you can use to create new Session objects.
SessionLocal = sessionmaker(
    autocommit=False, # You need to commit transactions for them to be processed
    autoflush=False, # Your changes are not automatically implemented in the database until they are committed
    bind=engine # Make it use our engine
)

# Creates a declarative base that all your schemas are based on
Base = declarative_base()

# Dependency for db related FastAPI routes that allow it to do DB operations with the created session
# Session is closed after the route finishes - Session created JIT for the route operation
def get_db():
    db = SessionLocal()  # Create a new session
    try:
        yield db  # Provide the session to the route without returning! Once route finishes, we continue the function
    finally:
        db.close()  # Closes the session after the route finishes

