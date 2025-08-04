#!/bin/bash
# Script to check duplicate tracking status in Docker
# Duplicate tracking has been completely removed from the system

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}🔄 Checking duplicate tracking status in Docker...${NC}"

# Check if we're in the right directory
if [ ! -f "compose.yml" ]; then
    echo -e "${RED}❌ Error: compose.yml not found. Please run this script from the project root directory.${NC}"
    exit 1
fi

# Determine which container to use
CONTAINER_NAME="data_fetcher"

# Check if dev container is running
if docker ps --format "table {{.Names}}" | grep -q "data_fetcher_dev"; then
    CONTAINER_NAME="data_fetcher_dev"
    echo -e "${GREEN}📦 Using development container: ${CONTAINER_NAME}${NC}"
else
    echo -e "${GREEN}📦 Using production container: ${CONTAINER_NAME}${NC}"
fi

# Check if container is running
if ! docker ps --format "table {{.Names}}" | grep -q "${CONTAINER_NAME}"; then
    echo -e "${RED}❌ Error: Container ${CONTAINER_NAME} is not running.${NC}"
    echo -e "${YELLOW}💡 Start the container first with: docker-compose up -d data_fetcher${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Container ${CONTAINER_NAME} is running${NC}"

# Run the status check script
echo -e "${YELLOW}🚀 Checking duplicate tracking status...${NC}"
docker exec -it "${CONTAINER_NAME}" python data_fetcher/reset_people_duplicates.py

echo -e "${GREEN}✅ Status check complete!${NC}"
echo -e "${YELLOW}💡 Duplicate tracking has been completely removed from the system.${NC}" 