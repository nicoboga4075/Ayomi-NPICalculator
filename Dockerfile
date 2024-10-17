# Get the light version of Python 3.9 runtime
FROM python:3.9-slim 

# Set the working directory in the container
WORKDIR /app 

# Copy the requirements file separately to avoid installation again
COPY requirements.txt .

# Install the dependencies without cache
RUN pip install --no-cache-dir -r requirements.txt 

 # Copy the current directory contents into the container at /app
COPY . . 

# Make port 8000 available outside this container
EXPOSE 8000 

# Launch Uvicorn server with app.py / app object on port 8000 for global host
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]