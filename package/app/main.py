import logging
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from app import __version__
from app.api import auth, backup, garmin, plans, profile, workouts
from app.core.database import Base, checkpoint, engine
from app.models.schemas import init_db_migrations
from app.schedulers.tasks import start_scheduler, stop_scheduler
from app.services.garmin_client import log_library_support

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")

Base.metadata.create_all(bind=engine)
init_db_migrations(engine)

app = FastAPI(title="Garmin Companion", version=__version__)
app.add_middleware(GZipMiddleware, minimum_size=1000)

for module in (auth, backup, garmin, profile, plans, workouts):
    app.include_router(module.router)

STATIC_DIR = Path(__file__).resolve().parent / "static"
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.on_event("startup")
def on_startup():
    log_library_support()
    start_scheduler()


@app.on_event("shutdown")
def on_shutdown():
    stop_scheduler()
    checkpoint()
    engine.dispose()


ASSETS = ("/static/css/app.css", "/static/js/help.js", "/static/js/app.js")


def _index_html() -> str:
    """index.html with the version in the CSS and JS URLs: each new version forces the browser
    (or the installed app) to download them instead of using its cached copy."""
    html = (STATIC_DIR / "index.html").read_text(encoding="utf-8")
    for path in ASSETS:
        html = html.replace(f'"{path}"', f'"{path}?v={__version__}"')
    return html


INDEX_HTML = _index_html()


@app.get("/")
def serve_index():
    return HTMLResponse(INDEX_HTML, headers={"Cache-Control": "no-cache"})


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8095, workers=1)
