from fastapi import HTTPException
from sqlalchemy import MetaData
from sqlalchemy.engine.url import URL
from sqlalchemy.ext.asyncio import create_async_engine
from dotenv import load_dotenv
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.declarative import declarative_base
import os
from rich import print

load_dotenv()
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DATABASE = os.getenv("DATABASE")

print(DB_USER, DB_PASSWORD, DB_HOST, DATABASE, DB_PORT)

# Check if required environment variables are set
if not all([DB_USER, DB_PASSWORD, DB_HOST, DATABASE, DB_PORT]):
    raise HTTPException(status_code=500, detail="Database configuration is missing some environment variables")
    
# Define MetaData
metadata = MetaData()

# Define individual connection parameters
connection_parameters = {
    'drivername': 'mysql+aiomysql',
    'username': DB_USER,
    'password': DB_PASSWORD,
    'host': DB_HOST,
    'port': DB_PORT,
    'database': DATABASE
}

# Build the connection URL dynamically using SQLAlchemy's URL helper
mysql_url = URL.create(**connection_parameters)

# Create an asynchronous engine using the dynamically built URL
engine = create_async_engine(mysql_url, echo=True)

# Create session factory
async_session = sessionmaker(bind=engine, class_= AsyncSession, expire_on_commit=False)

# Dependency to get database session
async def get_db():
    async with async_session() as session:
        yield session

Base = declarative_base()
