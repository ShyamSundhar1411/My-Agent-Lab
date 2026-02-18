import asyncio

from hypercorn.asyncio import serve
from hypercorn.config import Config

from src.main import app

if __name__ == "__main__":
    config = Config()
    config.bind = ["0.0.0.0:9000"]
    config.use_reloader = False
    asyncio.run(serve(app, config=config))
