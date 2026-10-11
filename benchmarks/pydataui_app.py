"""PyDataUI (pyrustapi) benchmark application for comparison with FastAPI."""
import asyncio
import time
from typing import List
from pydataui import App
from pydantic import BaseModel

app = App()


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


@app.api("/sync-get", method="GET", public=True)
def sync_get():
    return {
        "message": "Hello from PyDataUI",
        "framework": "pydataui",
        "status": "success",
        "timestamp": 1728640000,
    }


@app.api("/async-get", method="GET", public=True)
async def async_get():
    await asyncio.sleep(0.001)
    return {
        "message": "Hello async from PyDataUI",
        "framework": "pydataui",
        "status": "success",
        "timestamp": 1728640000,
    }


@app.api("/sync-post", method="POST", public=True)
def sync_post(book: BookInput):
    return BookOutput(
        id="book-pydataui-101",
        title=book.title,
        author=book.author,
        reading_time_hours=round(book.pages / 50.0, 2),
        status="registered",
    )


@app.api("/async-post", method="POST", public=True)
async def async_post(book: BookInput):
    await asyncio.sleep(0.001)
    return BookOutput(
        id="book-pydataui-102",
        title=book.title,
        author=book.author,
        reading_time_hours=round(book.pages / 50.0, 2),
        status="registered",
    )


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8002)
    args = parser.parse_args()
    app.run(port=args.port)
