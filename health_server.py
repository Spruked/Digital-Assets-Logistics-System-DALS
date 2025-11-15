#!/usr/bin/env python3
import json
from http.server import BaseHTTPRequestHandler, HTTPServer

class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/health":
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            response = {
                "status": "healthy",
                "phase": "11-A2",
                "predictive_engine": "enabled",
                "autonomous_mode": "active"
            }
            self.wfile.write(json.dumps(response).encode())
        else:
            self.send_response(404)
            self.end_headers()

if __name__ == "__main__":
    server = HTTPServer(("0.0.0.0", 8003), HealthHandler)
    print("Phase 11-A2 Test Server running on port 8003")
    server.serve_forever()