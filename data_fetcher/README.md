# LMU App Data Fetcher Service

The Data Fetcher service is responsible for collecting and synchronizing data from various external sources for the LMU App. It runs as a separate service and populates the shared database with up-to-date information.

## Table of Contents
- [LMU App Data Fetcher Service](#lmu-app-data-fetcher-service)
  - [Table of Contents](#table-of-contents)
  - [Overview](#overview)
  - [Architecture](#architecture)
    - [Core Components](#core-components)
      - [Base Collector (base\_collector.py)](#base-collector-base_collectorpy)
  - [Collectors](#collectors)
  - [Development](#development)
    - [Setting Up Local Development](#setting-up-local-development)
    - [Creating a New Collector](#creating-a-new-collector)
    - [Best Practices](#best-practices)
    - [Common Scheduling Patterns](#common-scheduling-patterns)
    - [Monitoring](#monitoring)

## Overview

The Data Fetcher service:
- Runs independently from the API service
- Collects data from multiple external sources
- Updates the shared database
- Supports both one-time and scheduled collection
- Handles graceful shutdown

## Architecture

```
data_fetcher/
├── src/
│   ├── core/
│   │   └── base_collector.py    # Base collector classes
│   ├── cinema/                  # Cinema data collector
│   ├── food/                    # Food/cafeteria data collector
│   ├── link/                    # External links collector
│   ├── roomfinder/             # Room information collector
│   ├── sport/                  # Sports facilities collector
│   ├── university/             # University data collector
│   └── main.py                 # Main application runner
└── tests/                      # Test suite
```

### Core Components

#### Base Collector (base_collector.py)

The service provides two base collector classes:

1. **BaseCollector**
   - Base class for one-time data collection
   - Implements core logging and error handling
   - Provides database session management

```python
from core.base_collector import BaseCollector

class YourCollector(BaseCollector):
    async def _collect_data(self, db):
        # Implement your collection logic here
        pass
```

2. **ScheduledCollector**
   - Extends BaseCollector for scheduled operations
   - Supports flexible scheduling using `schedule` library
   - Runs collection at specified intervals

```python
from core.base_collector import ScheduledCollector
import schedule

class YourScheduledCollector(ScheduledCollector):
    def __init__(self):
        job = schedule.every(1).hour
        super().__init__(job_schedule=job)

    async def _collect_data(self, db):
        # Implement your collection logic here
        pass
```

## Collectors

The service includes several specialized collectors:

1. **LinkCollector**
   - Collects external resource links
   - Updates shared link database

2. **UniversityCollector**
   - Gathers university-related information
   - Updates course and faculty data

3. **RoomfinderCollector**
   - Collects room information
   - Updates room availability and details

4. **FoodCollector**
   - Fetches cafeteria menus
   - Updates food and location data

5. **SportCollector**
   - Collects sports facility information
   - Updates course schedules and bookings

6. **CinemaCollector**
   - Gathers cinema schedules
   - Updates movie information

## Development

### Setting Up Local Development

1. Start the development container:
   ```bash
   docker compose up data_fetcher_dev db --build
   ```

2. The service will automatically:
   - Initialize the database connection
   - Create necessary tables
   - Start all configured collectors

### Creating a New Collector

1. Create a new module directory:
   ```
   data_fetcher/src/your_collector/
   ```

2. Implement your collector:
   ```python
   from core.base_collector import BaseCollector
   # or from core.base_collector import ScheduledCollector

   class YourCollector(BaseCollector):
       async def _collect_data(self, db):
           self.logger.info("Starting data collection")
           # Your collection logic here
           self.logger.info("Collection completed")
   ```

3. Add to main.py:
   ```python
   from data_fetcher.src.your_collector.collector import YourCollector

   class DataCollectorApp:
       def __init__(self):
           self.collectors = [
               # ... existing collectors ...
               YourCollector(),
           ]
   ```

### Best Practices

1. **Error Handling**
   - Use the built-in logging system
   - Handle collection-specific exceptions
   - Implement proper cleanup

2. **Database Operations**
   - Use the provided database session
   - Implement proper transaction handling
   - Clean up resources after use

3. **Scheduling**
   - Choose appropriate intervals
   - Consider data freshness requirements
   - Handle long-running operations

4. **Logging**
   - Use the collector's logger
   - Include relevant context
   - Use appropriate log levels


### Common Scheduling Patterns

- **Real-time data**: Every few minutes
- **Menu updates**: Daily at specific times
- **Course information**: Weekly during semester
- **Static data**: Once per startup

### Monitoring

The service provides logging with emoji indicators:
- 🔄 Collector starting
- ✅ Collection successful
- ⏹️ Collector shutting down
- 📅 Schedule information

Logs include:
- Collection status
- Next scheduled run
- Error details
- Performance metrics
