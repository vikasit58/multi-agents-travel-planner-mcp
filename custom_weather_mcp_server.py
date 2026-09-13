# pip install mcp requests
# With the help of FastMCP we can create custom MCP server
from mcp.server.fastmcp import FastMCP
import requests
import os

from dotenv import load_dotenv
load_dotenv()

# To create MCP server (Server Name)
mcp = FastMCP("Weather Server")

OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")

# Now we will create 2 tools 
# First to get current weather get_current_weather by city name
# Second Tool for Weather forcasting get_forecast by city name

#@mcp.tool() this very important Decorator by this line only Fast MCP will identify its tool for Weather MCP server, so for each tool we have to add decorator first.
@mcp.tool()
def get_current_weather(city: str):

    response = requests.get(
        "https://api.openweathermap.org/data/2.5/weather",
        params={
            "q": city,
            "appid": OPENWEATHER_API_KEY,
            "units": "metric"
        }
    )

    data = response.json()

    if response.status_code != 200:
        return data

    return {
        "city": data["name"],
        "temperature_c": data["main"]["temp"],
        "feels_like_c": data["main"]["feels_like"],
        "humidity": data["main"]["humidity"],
        "condition": data["weather"][0]["description"],
        "wind_speed": data["wind"]["speed"]
    }



@mcp.tool()
def get_forecast(city: str):

    url = (
        "https://api.openweathermap.org/data/2.5/forecast"
    )

    params = {
        "q": city,
        "appid": OPENWEATHER_API_KEY,
        "units": "metric"
    }

    response = requests.get(
        url,
        params=params
    )

    data = response.json()

    if response.status_code != 200 or "list" not in data:
        return data

    forecast = []

    # Return first 5 forecast entries
    for item in data["list"][:5]:

        forecast.append(
            {
                "datetime": item["dt_txt"],
                "temperature": item["main"]["temp"],
                "weather": item["weather"][0]["description"]
            }
        )

    return {
        "city": city,
        "forecast": forecast
    }




if __name__ == "__main__":
    mcp.run()