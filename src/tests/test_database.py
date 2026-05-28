from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

POSTGRES_USER_TEST = os.getenv('POSTGRES_USER_TEST')
POSTGRES_PASSWORD_TEST = os.getenv('POSTGRES_PASSWORD_TEST')
POSTGRES_HOST_TEST = os.getenv('POSTGRES_HOST_TEST')
POSTGRES_PORT_TEST = os.getenv('POSTGRES_PORT_TEST')
POSTGRES_DB_TEST = os.getenv('POSTGRES_DB_TEST')
SQLALCHEMY_TEST_DATABASE_URL = f"postgresql://{POSTGRES_USER_TEST}:{POSTGRES_PASSWORD_TEST}@{POSTGRES_HOST_TEST}:{POSTGRES_PORT_TEST}/{POSTGRES_DB_TEST}"

engine = create_engine(SQLALCHEMY_TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)