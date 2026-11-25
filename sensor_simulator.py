
import random
from datetime import datetime


def collect_sensor_data():

    sensor_data = {
        "temperature": round(random.uniform(20, 35), 1),
        "humidity": round(random.uniform(50, 95), 1),
        "soil_moisture": round(random.uniform(20, 90), 1),
        "leaf_wetness": round(random.uniform(10, 100), 1),

        "timestamp": datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )
    }

    return sensor_data
