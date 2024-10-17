from fastapi import FastAPI
from NPICalculator import models, views # MVC Design

# FastAPI Setup
app = FastAPI()

# Dependency
def get_db():
    db = models.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def index():
    return {"message" : "Welcome to FastAPI !"}

@app.post("/calculate")
def calculate():
    pass

@app.get('/results')
def get_results():
    pass

@app.get('/results/csv')
def download_results_csv():
    pass