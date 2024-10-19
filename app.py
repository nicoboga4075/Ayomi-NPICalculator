"""
This module runs the FastAPI application for the NPICalculator project.

It uses Uvicorn as the ASGI server to serve the application on
host 0.0.0.0 and port 8000.

"""
import uvicorn
from NPICalculator.controller import app # Gets FastAPI object from the controller

if __name__ == "__main__":
    # Launches Uvicorn server with app on port 8000 for global host
    uvicorn.run(app, host = "0.0.0.0", port = 8000)
