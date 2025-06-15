import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import httpx
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

# Initialize the FastAPI app with some basic info
app = FastAPI(
    title="Weather Information API",
    description="Check current weather for any city using real-time data from OpenWeatherMap.",
    version="1.0.0"
)

# Define what a weather report will look like in the response
class WeatherInfo(BaseModel):
    city: str
    temperature_celsius: float
    humidity_percent: int
    weather_description: str
    wind_speed_mps: float

# This function contacts the OpenWeatherMap API and gathers weather data for a city
async def fetch_weather(city_name: str) -> WeatherInfo:
    # Get your API key from environment variables
    api_key = os.getenv("OPENWEATHERMAP_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=500,
            detail="OpenWeatherMap API key is missing. Please set it in your environment variables."
        )

    # Set up the API request details
    api_url = "https://api.openweathermap.org/data/2.5/weather"
    query_parameters = {
        "q": city_name,
        "appid": api_key,
        "units": "metric"  # Get temperature in Celsius
    }

    # Send the request and handle the response
    async with httpx.AsyncClient() as client:
        response = await client.get(api_url, params=query_parameters)

        # Debugging information
        print("OpenWeatherMap status code:", response.status_code)
        print("Response text:", response.text)

        if response.status_code == 404:
            raise HTTPException(status_code=404, detail=f"City '{city_name}' not found.")
        if response.status_code != 200:
            raise HTTPException(status_code=502, detail="Something went wrong while fetching weather data.")

        # Extract the needed data from the JSON response
        data = response.json()
        weather_report = WeatherInfo(
            city=data.get("name"),
            temperature_celsius=data["main"]["temp"],
            humidity_percent=data["main"]["humidity"],
            weather_description=data["weather"][0]["description"].capitalize(),
            wind_speed_mps=data["wind"]["speed"]
        )
        return weather_report

# API endpoint to get weather info by city name
@app.get("/weather/{city_name}", response_model=WeatherInfo, summary="Get current weather for a city")
async def get_weather(city_name: str):

    return await fetch_weather(city_name)

# Default route — shows a welcome message
@app.get("/")
def welcome():
    return {
        "message": "👋 Welcome to the Weather Info API! Visit /weather/{city_name} to get live weather updates."
    }

# Run the app (useful when starting directly via Python)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("prodesk_task_02:app", host="0.0.0.0", port=8000, reload=True)
