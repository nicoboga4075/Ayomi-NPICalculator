# NPI Calculator with Python

This Python project is a **Reverse Polish Notation Calculator** (RPN or NPI in French) **API** built using **FastAPI** framework, **SQLite** database (powered by SQLAlchemy) and **MVC** design. The **REST** API supports basic mathematical operations and allows users to perform calculations. The project is containerized using **Docker** and managed via **docker-compose**.

## Features

- **Basic Operations** : Perform basic arithmetic calculations using Reverse Polish Notation
- **Database Support** : Store operations and their results in an SQLite database
- **Export to CSV** : Retrieve stored operations and results in CSV format
- **Dockerized** : Easily deploy the application in any environment using Docker
  
## Prerequisites

Before running this project, ensure you have the following installed:

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)
- [Git](https://git-scm.com/)

## Build and Run with Docker

To use the Dockerfile alone 

- Build the Docker image :

```
docker build -t npi-image:1.0 .
```
- Run the container :

```
docker run -p 8000:8000 --name npi-container npi-image:1.0
```

## Deploy with Docker Compose

To deploy with Docker Compose upon Dockerfile

```
docker-compose up --build
```
The FastAPI application will be running on http://localhost:8000.

To access the API from a different machine on the network, use the machine's IP address instead of localhost (e.g., http://<your-ip>:8000).


## Project Structure

### API Endpoints

- GET	**/results** :	Retrieves all stored calculations in the database
- GET	**/results/csv** :	Downloads all stored calculations as CSV
- POST	**/calculate** :	Performs a calculation

### Environment Variables

DATABASE_URL : Defines the database URL. The default is sqlite:///app.db, which uses an SQLite database.

### Running Tests
You can run the tests with :

```
docker-compose run test
```

The tests are managed by **doctest**, a lightweight built-in testing framework for Python.

### Accessing the API Documentation
FastAPI provides automatic interactive API documentation. You can access it by visiting the following links in your browser :

- **Swagger UI** : http://localhost:8000/docs
- **Redoc** : http://localhost:8000/redoc


