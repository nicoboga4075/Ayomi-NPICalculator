""" This module runs the FastAPI application for the NPICalculator project.
It uses Uvicorn as the ASGI server to serve the application.
"""
import subprocess
import sys
from NPICalculator.controller import app # Gets FastAPI object from the controller

def ensure_packages_installed(required_packages):
    """ Ensures that the specified packages are installed. """
    for package in required_packages:
        try:
            globals()[package] = __import__(package)  # Import the module dynamically
        except ImportError:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            globals()[package] = __import__(package)  # Re-imports after installation

ensure_packages_installed(["uvicorn", "fastapi", "sqlalchemy", "pandas"])

if __name__ == "__main__":
    import uvicorn
    # Launches Uvicorn server with app on port 8000 for global host
    uvicorn.run(app, host = "0.0.0.0", port = 8000)
