from dotenv import load_dotenv
from fastapi import FastAPI

load_dotenv()

from .routers import register_routers

app = FastAPI(title="Bili-Summarizer")
register_routers(app)
