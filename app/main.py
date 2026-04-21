from dotenv import load_dotenv
from fastapi import FastAPI

load_dotenv()

from app.api.router import api_router  # noqa: E402

app = FastAPI(title="政策解析", version="1.0.0")

app.include_router(api_router)
