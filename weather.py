from fastapi import FastAPI, HTTPException
import requests
import os

app = FastAPI()

# Replace this with your own OpenWeatherMap API key
API_KEY = "993aa40c60b3e4928023f7ab258561de"

@app.get("/weather")
def get_weather(region: str):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={region}&appid={API_KEY}&units=metric"
    response = requests.get(url)
    
    if response.status_code != 200:
        raise HTTPException(status_code=404, detail="Region not found or invalid API response.")
    
    data = response.json()
    
    weather_data = {
        "region": region,
        "temperature": data["main"]["temp"],
        "description": data["weather"][0]["description"],
        "humidity": data["main"]["humidity"],
        "wind_speed": data["wind"]["speed"]
    }

    return weather_data
