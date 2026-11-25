
# ==========================================
# SMARTCROP MONITORING SYSTEM
# CROP INTELLIGENCE AND DATA VALIDATION
# ==========================================


# 1. SENSOR DATA VALIDATION

def validate_sensor_data(data):

    required_fields = [
        "temperature",
        "humidity",
        "soil_moisture",
        "leaf_wetness"
    ]

    for field in required_fields:

        if field not in data:
            return False, f"Missing sensor data: {field}"

        value = data[field]

        if isinstance(value, bool) or not isinstance(value, (int, float)):
            return False, f"Invalid value for {field}"

        if not 0 <= value <= 100 and field != "temperature":
            return False, f"Value out of range for {field}"

        if not -50 <= value <= 60 and field == "temperature":
            return False, "Temperature value is out of range"

    return True, "Sensor data is valid"


# 2. CROP CONDITION ANALYSIS

def analyse_crop_conditions(data):

    # Validate data before analysis
    valid, message = validate_sensor_data(data)

    if not valid:
        raise ValueError(message)

    warnings = []
    recommendations = []

    temperature = data["temperature"]
    humidity = data["humidity"]
    soil_moisture = data["soil_moisture"]
    leaf_wetness = data["leaf_wetness"]


    # TEMPERATURE ANALYSIS

    if temperature > 32:

        warnings.append("High temperature detected.")

        recommendations.append(
            "Monitor crop temperature and consider suitable shading."
        )

    elif temperature < 18:

        warnings.append("Low temperature detected.")

        recommendations.append(
            "Monitor crop temperature and protect crops from cold conditions."
        )


    # AIR HUMIDITY ANALYSIS

    if humidity > 85:

        warnings.append("High air humidity detected.")

        recommendations.append(
            "Improve airflow around crops and monitor for fungal diseases."
        )


    # SOIL MOISTURE ANALYSIS

    if soil_moisture < 35:

        warnings.append("Low soil moisture detected.")

        recommendations.append(
            "Check irrigation and assess the soil water requirement."
        )


    # LEAF WETNESS ANALYSIS

    if leaf_wetness > 70:

        warnings.append("High leaf wetness detected.")

        recommendations.append(
            "Inspect cucumber leaves and improve airflow."
        )


    # SYSTEM STATUS CLASSIFICATION

    if len(warnings) >= 3:

        status = "HIGH PRIORITY"

    elif len(warnings) >= 1:

        status = "CAUTION"

    else:

        status = "NORMAL"

        recommendations.append(
            "Crop conditions are within the configured monitoring limits."
        )


    # RETURN ANALYSIS RESULTS

    return status, warnings, recommendations
