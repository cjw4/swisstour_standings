# This file defines the database connection string
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os

load_dotenv()

database = 'hoststar'

if database == 'mysql-local':
    prefix = 'mysql+mysqlconnector'
    DB_USER = 'root'
    DB_PASSWORD = ''
    DB_HOST = 'localhost'
    DB_NAME = 'wp_swisstour_2025'
elif database == 'postgres-local':
    prefix = 'postgresql+psycopg2'
    DB_USER = 'postgres'
    DB_PASSWORD = '1234'
    DB_HOST = 'localhost'
    DB_NAME = 'swisstour_2025'
elif database == 'hoststar':
    prefix = 'mysql+mysqlconnector'
    DB_USER = os.getenv('DB_USER')
    DB_PASSWORD = os.getenv('DB_PASSWORD')
    DB_HOST = os.getenv('DB_HOST')
    DB_NAME = os.getenv('DB_NAME')

# Create the database URL
DB_URL = f'{prefix}://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}' 

engine = create_engine(DB_URL)

try:
    with engine.connect() as connection:
        if database == 'hoststar':
            print("Connected successfully via SSH tunnel!")
except Exception as e:
    print(f"Connection failed: {e}")