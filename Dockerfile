# Gets the light version of Python 3.9 runtime
FROM python:3.9-slim 

# Sets the working directory in the container
WORKDIR /app 

# Copies the requirements file separately to avoid installation again
COPY requirements.txt .

# Installs the dependencies without cache
RUN pip install --no-cache-dir -r requirements.txt 

 # Copies the current directory contents into the container at /app
COPY . . 

# Makes port 8000 available outside this container
EXPOSE 8000 

# Launches Uvicorn server with app.py / app object on port 8000 for global host
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]