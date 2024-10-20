""" Controller for the app using FastAPI.

This module sets up the FastAPI application and defines endpoints for rendering 
views uppon models (MVC design).

>>> import fastapi
>>> fastapi_version = fastapi.__version__
>>> isinstance(fastapi_version, str)
True

>>> import pandas
>>> pandas_version = pandas.__version__
>>> isinstance(pandas_version, str)
True

"""
from io import StringIO
from time import time
import pandas as pd
from fastapi import FastAPI, Request, Depends, Form, status
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from NPICalculator import models, views # MVC Design
from NPICalculator.logger import logger # Custom logger

# FastAPI Setup
app = FastAPI(
    title="NPI Calculator API",
    description="This is a sample API to demonstrate Reverse Polish Notation.",
    version="1.0",
    contact={
        "name": "API Support",
        "email": "nicolas.bogalheiro@gmail.com",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    }
)

# CORS Setup
app.add_middleware(
    CORSMiddleware,
    allow_origins= ["http://localhost:8000"],
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "Authorization"],
    max_age= 24 * 60 * 60  # One day
)

# Basic Middleware Setup
async def dispatch(request: Request, call_next):
    """ Middleware function for logging request details in the FastAPI application.

    This function is executed for every incoming HTTP request. It records the start time,
    processes the request, and logs the HTTP method, request URL, and the time taken.

    """
    start_time = time()
    response = await call_next(request)
    process_time = time() - start_time
    log_dict = {
        "method": request.method,
        "url": request.url.path,
        "status_code": response.status_code,
        "process_time": process_time
    }
    if response.status_code == 200:
        logger.info("Request succeeded", extra=log_dict)
    else:
        logger.error("Request failed", extra=log_dict)
    return response

app.add_middleware(BaseHTTPMiddleware, dispatch = dispatch)

# Custom Open API Tags Setup
tags_metadata = [
    {
        "name": "Index",
        "description": "Home page with calculation form",
    },
    {
        "name": "Results",
        "description": "Operations history in the database",
    },
]
app.openapi_tags = tags_metadata

# Calculator Setup
engine = models.Calculator()

# Dependency
def get_db():
    """ Dependency that provides a database session.
    
    >>> import sqlalchemy
    >>> db = next(get_db()) 
    >>> isinstance(db, sqlalchemy.orm.session.Session)
    True
    >>> db.close()
    
    """
    db = models.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Gives access to static directory at the beginning
@app.on_event("startup")
def startup_event():
    """ Mounts the static directory to serve static files on startup.
    
    >>> app = FastAPI()
    >>> startup_event()
    >>> import os
    >>> os.path.exists(os.path.join("NPICalculator/static", "favicon.ico"))
    True
    
    """
    logger.info("Started API.")
    app.mount("/static", StaticFiles(directory="NPICalculator/static"), name="static")
    logger.info("Mounted static files.")

# Endpoints
@app.get("/", response_class=HTMLResponse, status_code=status.HTTP_200_OK,
description = "Renders the index page with a welcome message.", tags = ["Index"])
def index(request : Request):
    """ 
    >>> from unittest.mock import MagicMock
    >>> request = MagicMock()
    >>> response = index(request)
    >>> response.status_code == 200
    True
    >>> "Welcome to NPI Calculator Tool !" in response.body.decode()
    True
    """
    message = "Welcome to NPI Calculator Tool !"
    icon = "info"
    response = views.IndexView().render(request, message = message, icon = icon)
    return response

@app.get("/home", response_class=HTMLResponse, status_code=status.HTTP_200_OK,
description = "Renders the home page (same as / but without welcome message.", tags = ["Index"])
def home(request : Request):
    """
    >>> from unittest.mock import MagicMock
    >>> request = MagicMock()
    >>> response = home(request)
    >>> response.status_code == 200
    True
    """
    response = views.IndexView().render(request, message = None, icon = None)
    return response

@app.post("/calculate", response_class=HTMLResponse, status_code = status.HTTP_200_OK,
description = "Calculates the expression and stores it with result if success.", tags = ["Index"])
def calculate(request : Request, expression = Form(...), db = Depends(get_db)):
    """
    >>> from unittest.mock import MagicMock
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
            logger.info(message)
    except ValueError as e:
        logger.error(str(e))
    response = views.IndexView().render(request, message = message, icon = icon)
    return response

@app.get('/results', response_class=HTMLResponse, status_code=status.HTTP_200_OK,
description = "Retrieves results from the database and renders them.", tags = ["Results"])
def get_results(request : Request, db = Depends(get_db)):
    """ 
    >>> from unittest.mock import MagicMock
    >>> request = MagicMock()
    >>> db = MagicMock()
    >>> db.query().all.return_value = [models.Operation(expression="3 4 +", result=7.0)]
    >>> response = get_results(request, db)
    >>> response.status_code == 200
    True
    >>> len(response.body.decode()) > 0
    True
    """
    results = db.query(models.Operation).all()
    response = views.ResultsView().render(request, results = results)
    return response

@app.get('/results/csv', response_class=StreamingResponse, status_code=status.HTTP_200_OK,
description = "Downloads the operation history as a CSV file.", tags = ["Results"])
def download_results_csv(db  = Depends(get_db)):
    """
    >>> from unittest.mock import MagicMock
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
    response = StreamingResponse(csv_io, media_type="text/csv", headers=headers)
    return response
    