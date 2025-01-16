# LMU App Backend

This is the backend service for the LMU App. It provides the necessary API endpoints and data processing for the LMU application.

## Table of Contents
- [Prerequisites](#prerequisites)
- [Installation](#installation)
  - [Using Python Virtual Environment](#using-python-virtual-environment)
  - [Using Docker Compose](#using-docker-compose)
- [Usage](#usage)

## Prerequisites

Before you begin, ensure you have met the following requirements:
* You have installed the latest version of [Python](https://www.python.org/downloads/) (3.12 recommended)
* (Optional) You have installed [Docker](https://www.docker.com/get-started) and [Docker Compose](https://docs.docker.com/compose/install/)
* You have a Windows/Linux/Mac machine.
* You have read the LMU App documentation (if available).

## Installation

### Using Python Virtual Environment

1. Clone the repository:
   ```
   git clone https://github.com/lmu-devs/lmu_app_backend.git
   cd lmu-app-backend
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   ```

3. Activate the virtual environment:
   - On Windows:
     ```
     venv\Scripts\activate
     ```
   - On macOS and Linux:
     ```
     source venv/bin/activate
     ```

4. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

5. Run docker compose:
   ```
   docker-compose build
   docker-compose up -d
   ```

### Using Docker Compose

1. Clone the repository:
   ```
   git clone https://github.com/lmu-devs/lmu_app_backend.git
   cd lmu-app-backend
   ```

2. Build and run the Docker containers:
   ```
   docker-compose up --build
   ```

   This command will build the Docker image and start the containers defined in your `docker-compose.yml` file.

## Usage

To run the LMU App Backend, follow these steps:

1. If using virtual environment, make sure it's activated.
2. Run the main application:
   ```
   python app.py
   ```

If using Docker Compose:
```
docker-compose up
```

Swagger UI should be accessible at `http://localhost:8001/v1/docs`
REST API should now be running and accessible at `http://localhost:8001/v1`
PgAdmin should now be running and accessible at `http://localhost:5050`
