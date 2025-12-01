import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pathlib import Path

app = FastAPI(title="DALS Dashboard")

# Setup templates
templates_dir = Path(__file__).parent / "iss_module" / "templates"
templates = Jinja2Templates(directory=str(templates_dir))

# Mount static files
static_dir = Path(__file__).parent / "iss_module" / "static"
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Serve the DALS dashboard"""
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.get("/login", response_class=HTMLResponse)
async def login(request: Request):
    """Serve the login page"""
    return templates.TemplateResponse("login.html", {"request": request})

if __name__ == "__main__":
    print("Starting DALS Dashboard on http://0.0.0.0:8008")
    uvicorn.run(app, host="0.0.0.0", port=8008, log_level="info")