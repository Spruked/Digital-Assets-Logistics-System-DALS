"""
CSMM Service Runner

Standalone runner for the Caleon Self-Maintenance Module FastAPI service.
"""

import uvicorn
import logging
from iss_module.csmm.csmm_api import app

if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Run the CSMM FastAPI service
    uvicorn.run(
        "iss_module.csmm.csmm_api:app",
        host="0.0.0.0",
        port=8009,
        reload=True,
        log_level="info"
    )