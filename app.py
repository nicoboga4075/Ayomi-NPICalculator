from NPICalculator.controller import app # Get FastAPI object from the controller
import uvicorn

if __name__ == "__main__":
    uvicorn.run("app:app", host = "0.0.0.0", port = 8000) # Launch Uvicorn server with current and app object on port 8000 for global host