"""
Test configurations for different scenarios
"""

LIGHT_LOAD = {
    "users": 10,
    "spawn_rate": 1,
    "run_time": "1m"
}

MEDIUM_LOAD = {
    "users": 50,
    "spawn_rate": 5,
    "run_time": "5m"
}

HEAVY_LOAD = {
    "users": 100,
    "spawn_rate": 10,
    "run_time": "10m"
}

SPIKE_TEST = {
    "users": 200,
    "spawn_rate": 20,
    "run_time": "2m"
}