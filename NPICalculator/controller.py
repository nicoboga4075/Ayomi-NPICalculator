import pandas as pd
from io import StringIO
from fastapi import FastAPI, HTTPException, Request, Depends, Form
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from NPICalculator import models, views # MVC Design

# FastAPI Setup
app = FastAPI()

# Gives access to static directory
app.mount("/static", StaticFiles(directory="NPICalculator/static"), name="static")

# Dependency
def get_db():
    db = models.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Calculator Setup
engine = models.Calculator()

# Endpoints
@app.get("/", response_class=HTMLResponse)
def index(request : Request):
    return views.IndexView().render(request, "Welcome to NPI Calculator Tool ! ", "info")  
   
@app.post("/calculate", response_class=HTMLResponse)
def calculate(request : Request, expression = Form(...), db = Depends(get_db)):
    message = "Invalid expression"
    icon = "error"
    try:
        # Computes the result using the engine
        result = engine.compute(expression)
        if result:
            # Stores the operation in the database
            op = models.Operation(expression = expression, result = result)
            engine.save(op, db)
            message = f"{expression} = {result}"
            icon = "success"
    except Exception as e:
        pass
    return views.IndexView().render(request, message, icon)      

@app.get('/results', response_class=HTMLResponse)
def get_results(request : Request, db = Depends(get_db)):
    results = db.query(models.Operation).all()
    return views.ResultsView().render(request, results)

@app.get('/results/csv')
def download_results_csv(db  = Depends(get_db)):
    # Converts the data to a pandas DataFrame
    operations = db.query(models.Operation).all()
    data = [{"expression": op.expression, "result": op.result} for op in operations]

    # Creates a Pandas DataFrame with two columns: expression and result
    df = pd.DataFrame(data, columns=["expression", "result"])
    # Uses StringIO to capture the CSV data in-memory
    csv_io = StringIO()
    df.to_csv(csv_io, index=False)
    csv_io.seek(0)  # Moves to the beginning of the StringIO buffer

    # Sends CSV as a StreamingResponse
    headers = {
        'Content-Disposition': 'attachment; filename="results.csv"'
    }
    return StreamingResponse(csv_io, media_type="text/csv", headers=headers)