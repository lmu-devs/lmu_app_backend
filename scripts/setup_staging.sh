#!/bin/bash

# Exit on error
set -e

# Update system packages
echo "Updating system packages..."
apt-get update
apt-get upgrade -y

# Install Docker and Docker Compose
echo "Installing Docker and Docker Compose..."
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

# Add the repository to Apt sources:
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "${UBUNTU_CODENAME:-$VERSION_CODENAME}") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update

 sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin


# Create app directory
echo "Creating app directory..."
mkdir -p /opt/lmu_app_backend
cd /opt/lmu_app_backend

# Clone the repository
# echo "Cloning the repository..."
# git clone https://github.com/lmu-devs/lmu_app_backend.git .
# git checkout staging

# Create environment file - Manual step!
echo "Create environment file..."
touch .env

# Start the application
echo "Starting the application..."
docker compose up -d --build

# Run database migrations
echo "Running database migrations..."
docker exec api_v1 alembic upgrade head

echo "Staging environment setup complete!"
echo "The API should now be accessible at https://api.staging.lmu-dev.org" 