import subprocess
import sys
from api.tests.v1.performance.locust_config import *

from shared.src.core.settings import get_settings

def run_locust_test(config, test_name):
    """Run a locust test with given configuration"""
    cmd = [
        "locust",
        "-f", "api/tests/v1/performance/wishlist/locustfile.py",
        "--headless",
        "--users", str(config["users"]),
        "--spawn-rate", str(config["spawn_rate"]),
        "--run-time", config["run_time"],
        "--host", "http://localhost:8001/v1",
        "--html", f"report_{test_name}.html"
    ]
    
    subprocess.run(cmd)

if __name__ == "__main__":
    test_type = sys.argv[1] if len(sys.argv) > 1 else "light"
    
    configs = {
        "light": LIGHT_LOAD,
        "medium": MEDIUM_LOAD,
        "heavy": HEAVY_LOAD,
        "spike": SPIKE_TEST
    }
    
    config = configs.get(test_type, MEDIUM_LOAD)
    run_locust_test(config, test_type)