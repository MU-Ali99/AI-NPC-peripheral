import uvicorn

from .app import app
from .config import Settings


def main() -> None:
    settings = Settings.load()
    uvicorn.run(
        app,
        host=settings.bridge_host,
        port=settings.bridge_port,
        log_level="info",
    )


if __name__ == "__main__":
    main()
