import os
import requests

API_KEY = os.getenv("API_KEY")
if not API_KEY:
    raise RuntimeError("API_KEY not set or empty")

LAT = 25.7642647 
LON = -80.802024966

BASE_URL = "https://api.openweathermap.org/data/2.5/air_pollution"

def fetch_pollutant_data(lat, lon):
    params = {
        "lat": lat,
        "lon": lon,
        "appid": API_KEY
    }

    response = requests.get(BASE_URL, params=params)
    response.raise_for_status()
    data = response.json()

    return data["list"][0]["components"]

def compute_pm25_aqi(pm25):
    """
    Compute AQI from PM2.5 concentration (µg/m³)
    using US EPA breakpoints.
    """

    breakpoints = [
        (0.0, 12.0, 0, 50, "Good"),
        (12.1, 35.4, 51, 100, "Moderate"),
        (35.5, 55.4, 101, 150, "Unhealthy for Sensitive Groups"),
        (55.5, 150.4, 151, 200, "Unhealthy"),
        (150.5, 250.4, 201, 300, "Very Unhealthy"),
        (250.5, 500.4, 301, 500, "Hazardous"),
    ]

    for c_low, c_high, aqi_low, aqi_high, category in breakpoints:
        if c_low <= pm25 <= c_high:
            aqi = ((aqi_high - aqi_low) / (c_high - c_low)) * (pm25 - c_low) + aqi_low
            return round(aqi), category

    return None, "Out of Range"

def present_result(pm25, aqi, category):
    print(f"Location     : Fixed Coordinates")
    print(f"PM2.5 (µg/m³): {pm25}")
    print(f"AQI          : {aqi}")
    print(f"Category     : {category}")

def run_agent():
    pollutants = fetch_pollutant_data(LAT, LON)
    pm25 = pollutants["pm2_5"]

    aqi, category = compute_pm25_aqi(pm25)
    present_result(pm25, aqi, category)


if __name__ == "__main__":
    run_agent()