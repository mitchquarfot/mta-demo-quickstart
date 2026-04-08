from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path
import os

from routes.kpis import router as kpis_router
from routes.attribution import router as attribution_router
from routes.channels import router as channels_router
from routes.paths import router as paths_router
from routes.frequency import router as frequency_router
from routes.incrementality import router as incrementality_router
from routes.mmm import router as mmm_router
from routes.campaigns import router as campaigns_router
from routes.identity import router as identity_router
from routes.forecast import router as forecast_router
from routes.propensity import router as propensity_router
from routes.optimizer import router as optimizer_router
from routes.agent import router as agent_router

app = FastAPI(title="MTA Dashboard API", version="1.0.0")

@app.get("/healthz")
def health():
    return {"status": "ok"}

app.include_router(kpis_router)
app.include_router(attribution_router)
app.include_router(channels_router)
app.include_router(paths_router)
app.include_router(frequency_router)
app.include_router(incrementality_router)
app.include_router(mmm_router)
app.include_router(campaigns_router)
app.include_router(identity_router)
app.include_router(forecast_router)
app.include_router(propensity_router)
app.include_router(optimizer_router)
app.include_router(agent_router)

STATIC_DIR = Path(__file__).parent / "static"

if STATIC_DIR.exists():
    app.mount("/assets", StaticFiles(directory=STATIC_DIR / "assets"), name="assets")

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        file_path = STATIC_DIR / full_path
        if file_path.exists() and file_path.is_file():
            return FileResponse(file_path)
        return FileResponse(STATIC_DIR / "index.html")
