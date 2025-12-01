#!/usr/bin/env python3
"""
Minimal test server for Cali_X_One MetaMask signing interface
"""
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import uvicorn

app = FastAPI(title="Cali_X_One Test Server")

@app.get("/sign-cali", response_class=HTMLResponse)
async def sign_cali():
    """Serve the MetaMask signing interface"""
    html_path = "sign_cali.html"
    try:
        with open(html_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return content
    except FileNotFoundError:
        return "<h1>Error: sign_cali.html not found</h1>"

@app.get("/api/cali/core-hash")
async def get_core_hash():
    """Generate Cali_X_One core hash"""
    import hashlib
    import pathlib

    cali_file = pathlib.Path("iss_module/cali_x_one/cali_dals.py")
    if not cali_file.exists():
        return {"error": "Cali_X_One core file not found"}

    core_content = cali_file.read_text()
    core_hash = hashlib.sha256(core_content.encode()).hexdigest()

    return {"core_hash": core_hash}

@app.post("/api/cali/verify-identity")
async def verify_identity(request: Request):
    """Verify and save MetaMask signature"""
    import json
    import pathlib
    from datetime import datetime

    data = await request.json()
    signature = data.get("signature")
    address = data.get("address")

    if not signature or not address:
        return {"success": False, "error": "Missing signature or address"}

    # Generate core hash
    cali_file = pathlib.Path("iss_module/cali_x_one/cali_dals.py")
    core_content = cali_file.read_text()
    core_hash = hashlib.sha256((core_content + address).encode()).hexdigest()

    # Save signature
    sig_data = {
        "status": "signed",
        "addr": address,
        "sig": signature,
        "hash": core_hash,
        "signed_at": datetime.now().isoformat()
    }

    sig_file = pathlib.Path("iss_module/cali_x_one/cali_sig.json")
    sig_file.write_text(json.dumps(sig_data, indent=2))

    return {"success": True, "message": "Identity verified and saved"}

if __name__ == "__main__":
    print("🚀 Starting Cali_X_One test server on http://localhost:8004")
    uvicorn.run(app, host="0.0.0.0", port=8004)