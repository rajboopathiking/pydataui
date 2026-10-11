"""FastAPI benchmark application for comparison with PyDataUI."""
import asyncio
import time
from typing import List
from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn

app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)


class BookInput(BaseModel):
    title: str
    author: str
    pages: int
    rating: float
    tags: List[str]


class BookOutput(BaseModel):
    id: str
    title: str
    author: str
    reading_time_hours: float
    status: str


@app.get("/sync-get")
def sync_get():
    return {
        "message": "Hello from FastAPI",
        "framework": "fastapi",
        "status": "success",
        "timestamp": 1728640000,
    }


@app.get("/async-get")
async def async_get():
    await asyncio.sleep(0.001)
    return {
        "message": "Hello async from FastAPI",
        "framework": "fastapi",
        "status": "success",
        "timestamp": 1728640000,
    }


@app.post("/sync-post")
def sync_post(book: BookInput):
    return BookOutput(
        id="book-fastapi-101",
        title=book.title,
        author=book.author,
        reading_time_hours=round(book.pages / 50.0, 2),
        status="registered",
    )


@app.post("/async-post")
async def async_post(book: BookInput):
    await asyncio.sleep(0.001)
    return BookOutput(
        id="book-fastapi-102",
        title=book.title,
        author=book.author,
        reading_time_hours=round(book.pages / 50.0, 2),
        status="registered",
    )


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8001)
    args = parser.parse_args()
    uvicorn.run(app, host="127.0.0.1", port=args.port, log_level="error", loop="uvloop")
