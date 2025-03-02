# LMU App Backend

This is the backend service for the LMU App. It provides the necessary API endpoints and data processing for the LMU application.

## Table of Contents
- [LMU App Backend](#lmu-app-backend)
  - [Table of Contents](#table-of-contents)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
    - [Using Python Virtual Environment](#using-python-virtual-environment)
    - [Using Docker Compose](#using-docker-compose)
  - [Environments](#environments)
    - [Development](#development)
    - [Staging](#staging)
    - [Production](#production)
  - [Branching Strategy](#branching-strategy)
  - [CI/CD Pipeline](#cicd-pipeline)
  - [Deployment Workflow](#deployment-workflow)
    - [Environments](#environments-1)
    - [Branching Strategy](#branching-strategy-1)
    - [Deployment Process](#deployment-process)
    - [Manual Deployment](#manual-deployment)
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

## Environments

The application supports three environments:

### Development

The development environment is used for local development and testing.

1. Copy the environment template:
   ```
   cp .env.template .env
   ```

2. Run the application using Docker Compose:
   ```
   docker compose up --build
   ```

### Staging

The staging environment is hosted on a Digital Ocean droplet and is used for testing features before they are deployed to production.

- URL: `api.staging.lmu-dev.org`
- Deployment: Automatic when code is pushed to the `staging` branch

To deploy manually to staging:
```
docker compose -f compose.staging.yml up -d --build
```

### Production

The production environment is hosted on a Digital Ocean droplet and is the live environment used by end users.

- URL: `api.lmu-dev.org`
- Deployment: Automatic when code is pushed to the `main` branch

To deploy manually to production:
```
docker compose -f compose.production.yml up -d --build
```

## Branching Strategy

We follow a simple branching strategy:

1. `main` - Production branch. Represents the code currently in production.
2. `staging` - Staging branch. Used for testing features before they are deployed to production.
3. Feature branches - Created from `staging` for new features or bug fixes.

Workflow:
1. Create a feature branch from `staging`
2. Develop and test your feature
3. Create a pull request to merge into `staging`
4. After testing in staging, create a pull request to merge `staging` into `main`

## CI/CD Pipeline

We use GitHub Actions for continuous integration and deployment:

1. **CI Tests**: Run on pull requests to `staging` and `main` branches
2. **Staging Deployment**: Automatically deploys to staging when code is pushed to the `staging` branch
3. **Production Deployment**: Automatically deploys to production when code is pushed to the `main` branch

## Deployment Workflow

This project uses a multi-environment deployment strategy with Docker images:

### Environments

- **Development**: Local environment for development
- **Staging**: Hosted environment for testing (`service.staging.xxx.org`)
- **Production**: Production environment (`api.xxx.org`)

### Branching Strategy

- **`main`**: Production-ready code, always stable
- **`staging`**: Integration branch for testing before production
- Feature branches should be created from and merged back to `staging`

### Deployment Process

1. **Development**:
   - Run locally using `docker compose up`

2. **Staging**:
   - Push changes to the `staging` branch
   - GitHub Actions will:
     - Build Docker images
     - Tag images with both `staging` and the commit SHA
     - Push images to Docker Hub
     - Deploy to the staging server

3. **Production**:
   - Push changes to the `main` branch (or use the GitHub workflow dispatch)
   - GitHub Actions will:
     - Pull the same Docker images that were tested in staging
     - Tag them as `production`
     - Deploy to the production server

This ensures that the exact same code that was tested in staging is deployed to production.

### Manual Deployment

You can also trigger a production deployment manually with a specific commit SHA:

1. Go to GitHub Actions
2. Select the "Deploy to Production" workflow
3. Click "Run workflow"
4. Enter the specific commit SHA to deploy (optional)
5. Click "Run workflow"

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
