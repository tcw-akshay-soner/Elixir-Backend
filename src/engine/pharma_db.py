from sqlalchemy import MetaData
from sqlalchemy.engine.url import URL
from sqlalchemy.ext.asyncio import create_async_engine
from dotenv import load_dotenv
import os

load_dotenv()
username = os.getenv("NAME")
password = os.getenv("PASSWORD")
host = os.getenv("HOST")
port = os.getenv("PORT")
database = os.getenv("DATABASE")
print(username,password,host,port, database)
# Define MetaData
metadata = MetaData()

# Define individual connection parameters
connection_parameters = {
    'drivername': 'mysql+aiomysql',
    'username': username,
    'password': password,
    'host': host,
    'port': port,
    'database': database
}

# Build the connection URL dynamically using SQLAlchemy's URL helper
mysql_url = URL.create(**connection_parameters)

# Create an asynchronous engine using the dynamically built URL
engine = create_async_engine(mysql_url, echo=True)
