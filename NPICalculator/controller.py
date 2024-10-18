from NPICalculator import models, views # MVC Design
from io import StringIO
import pandas as pd
from fastapi import FastAPI, Request, Depends, Form
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from unittest.mock import MagicMock

# FastAPI Setup
app = FastAPI()

# Calculator Setup
engine = models.Calculator()

# Dependency
def get_db():
    db = models.SessionLocal() 
    try:
        yield db
    finally:
        db.close()

# Gives access to static directory at the beginning
@app.on_event("startup")
def startup_event():
    app.mount("/static", StaticFiles(directory="NPICalculator/static"), name="static")

# Endpoints
@app.get("/", response_class=HTMLResponse)
def index(request : Request):
    """Renders the index page with a welcome message.

    >>> request = MagicMock()
    >>> response = index(request)
    >>> response.status_code == 200
    True
    >>> "Welcome to NPI Calculator Tool !" in response.body.decode()
    True

    """
    return views.IndexView().render(request, "Welcome to NPI Calculator Tool !")

@app.get("/home", response_class=HTMLResponse)
def home(request : Request):
    """ Renders the home page.
    
    >>> request = MagicMock()
    >>> response = home(request)
    >>> response.status_code == 200
    True

    """
    return views.IndexView().render(request)  
   
@app.post("/calculate", response_class=HTMLResponse)
def calculate(request : Request, expression = Form(...), db = Depends(get_db)):
    """ Calculates the expression and stores it in the database.
    
    >>> request = MagicMock()
    >>> request.form = MagicMock(return_value={"expression": "1 1 +"})
    >>> db = MagicMock()
    >>> response = calculate(request, "1 1 +", db)
    >>> "1 1 + = 2.0" in response.body.decode()
    True
    
    >>> request.form = MagicMock(return_value={"expression": "invalid_expression"})
    >>> response = calculate(request, "invalid_expression", db)
    >>> "Invalid expression" in response.body.decode()
    True

    >>> request.form = MagicMock(return_value={"expression": "3 4 + 2 *"})
    >>> response = calculate(request, "3 4 + 2 *", db)
    >>> "3 4 + 2 * = 14.0" in response.body.decode()
    True

    >>> request.form = MagicMock(return_value={"expression": "10 2 / 3 +"})
    >>> response = calculate(request, "10 2 / 3 +", db)
    >>> "10 2 / 3 + = 8.0" in response.body.decode()
    True

    >>> request.form = MagicMock(return_value={"expression": "5 6 - 2 *"})
    >>> response = calculate(request, "5 6 - 2 *", db)
    >>> "5 6 - 2 * = -2.0" in response.body.decode()
    True

    >>> request.form = MagicMock(return_value={"expression": "-5.5 -2.5 +"})
    >>> response = calculate(request, "-5.5 -2.5 +", db)
    >>> "-5.5 -2.5 + = -8.0" in response.body.decode()
    True

    >>> request.form = MagicMock(return_value={"expression": "-10 -2 *"})
    >>> response = calculate(request, "-10 -2 *", db)
    >>> "-10 -2 * = 20.0" in response.body.decode()
    True

    >>> request.form = MagicMock(return_value={"expression": "+0 +0 -"})
    >>> response = calculate(request, "+0 +0 -", db)
    >>> "+0 +0 - = 0.0" in response.body.decode()
    True

    >>> request.form = MagicMock(return_value={"expression": "0 0 +"})
    >>> response = calculate(request, "0 0 +", db)
    >>> "0 0 + = 0.0" in response.body.decode()
    True

    >>> request.form = MagicMock(return_value={"expression": "8 0 /"})
    >>> response = calculate(request, "8 0 /", db)
    >>> "Invalid expression" in response.body.decode()
    True

    """
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
        return views.IndexView().render(request, str(e), icon)
    return views.IndexView().render(request, message, icon)      

@app.get('/results', response_class=HTMLResponse)
def get_results(request : Request, db = Depends(get_db)):
    """ Retrieves results from the database and renders them.
    
    >>> request = MagicMock()
    >>> db = MagicMock()
    >>> db.query().all.return_value = [models.Operation(expression="3 4 +", result=7.0), models.Operation(expression="6 3 *", result=18.0)]
    >>> response = get_results(request, db)
    >>> response.status_code == 200
    True
    >>> len(response.body.decode()) > 0
    True

    """
    results = db.query(models.Operation).all()
    return views.ResultsView().render(request, results)

@app.get('/results/csv')
def download_results_csv(db  = Depends(get_db)):
    """ Downloads the operation history as a CSV file.
    
    >>> db = MagicMock()
    >>> db.query().all.return_value = [models.Operation(expression="3 + 4", result=7)]
    >>> response = download_results_csv(db)
    >>> response.status_code == 200
    True
    >>> response.headers['Content-Disposition'] == 'attachment; filename="history.csv"'
    True

    """
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
        'Content-Disposition': 'attachment; filename="history.csv"'
    }
    return StreamingResponse(csv_io, media_type="text/csv", headers=headers)
    