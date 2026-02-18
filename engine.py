from sqlalchemy import create_engine
from dotenv import load_dotenv
import os

load_dotenv()

url = os.getenv("url")

engine = create_engine(url, echo=True)
