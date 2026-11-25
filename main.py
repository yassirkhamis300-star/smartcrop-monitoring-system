
# ==========================================
# SMARTCROP MONITORING SYSTEM
# MAIN APPLICATION
# ==========================================

import time

from sensor_simulator import collect_sensor_data
from analysis import analyse_crop_conditions

from modules.database import (
    create_database,
    save_sensor_data,
    get_record_count
)


def display_sensor_data(data):

    print("\n================================")
    print("       SENSOR READINGS")
    print("================================")

    print("Temperature:", data["temperature"], "°C")
    print("Humidity:", data["humidity"], "%")
    print("Soil Moisture:", data["soil_moisture"], "%")
    print("Leaf Wetness:", data["leaf_wetness"], "%")
    print("Timestamp:", data["timestamp"])


def display_analysis(status, warnings, recommendations):

    print("\n================================")
    print("       CROP INTELLIGENCE")
    print("================================")

    print("System Status:", status)

    print("\nWARNINGS")

    if warnings:
        for warning in warnings:
            print("[WARNING]", warning)
    else:
        print("No warnings detected.")

    print("\nSMART RECOMMENDATIONS")

    for recommendation in recommendations:
        print("[ADVICE]", recommendation)


def run_monitoring():

    # Create database
    create_database()

    print("\n================================")
    print("   SMARTCROP MONITORING SYSTEM")
    print("================================")

    print("Monitoring started successfully.")
    print("Using simulated sensor data.")
    print("Press CTRL + C to stop monitoring.")

    try:

        while True:

            # 1. Collect sensor data
            data = collect_sensor_data()

            # 2. Analyse crop conditions
            status, warnings, recommendations = (
                analyse_crop_conditions(data)
            )

            # 3. Save data into database
            save_sensor_data(data, status)

            # 4. Display sensor readings
            display_sensor_data(data)

            # 5. Display analysis and recommendations
            display_analysis(
                status,
                warnings,
                recommendations
            )

            # 6. Display database information
            total_records = get_record_count()

            print("\nTotal Database Records:", total_records)

            print("\nNext monitoring in 5 seconds...")
            print("--------------------------------")

            # Wait for next reading
            time.sleep(5)

    except KeyboardInterrupt:

        print("\n\nMonitoring stopped successfully.")
        print("Thank you for using SmartCrop.")

    except Exception as error:

        print("\nSYSTEM ERROR:", error)
        print("Please check your project files.")


# ==========================================
# APPLICATION ENTRY POINT
# ==========================================

if __name__ == "__main__":

    run_monitoring()
