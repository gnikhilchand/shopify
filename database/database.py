# from sqlalchemy import create_engine, Engine
# from sqlalchemy.orm import sessionmaker, declarative_base
# import os

# # 1. Define your Database URL
# # It's best practice to use an environment variable for this.
# # Format: "mysql+pymysql://<user>:<password>@<host>/<dbname>"
# DATABASE_URL = os.getenv("DATABASE_URL", "mysql+pymysql://root:password@127.0.0.1/shopify_insights")

# # 2. Create the SQLAlchemy engine
# # The engine is the entry point to the database.
# engine: Engine = create_engine(DATABASE_URL)

# # 3. Create a SessionLocal class
# # Each instance of SessionLocal will be a database session.
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# # 4. Create a Base class
# # Our database model classes will inherit from this class.
# Base = declarative_base()

# # FastAPI Dependency to get a DB session for each request
# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "mysql+pymysql://user:password@localhost/shopify_db")

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()