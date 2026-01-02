"""Weather and external data integration for Supply Chain Guardian."""
import os
import requests
from typing import Dict, Any, List
from datetime import datetime, timedelta
import json

class WeatherService:
    """Integrates with OpenWeatherMap API for real-time weather data."""
    
    def __init__(self, api_key: str = None):
        """Initialize weather service with API key."""
        self.api_key = api_key or os.getenv("WEATHER_API_KEY")
        self.base_url = "https://api.openweathermap.org/data/2.5"
        
        if not self.api_key:
            print("⚠️ Warning: WEATHER_API_KEY not set. Using mock data.")
            self.mock_mode = True
        else:
            self.mock_mode = False
    
    def get_current_weather(self, location: str) -> Dict[str, Any]:
        """Get current weather for a location."""
        if self.mock_mode:
            return self._get_mock_weather(location)
        
        try:
            # Parse location (city, country)
            city = location.split(",")[0].strip()
            
            url = f"{self.base_url}/weather"
            params = {
                "q": city,
                "appid": self.api_key,
                "units": "metric"
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            return {
                "location": location,
                "temperature": data["main"]["temp"],
                "condition": data["weather"][0]["main"],
                "description": data["weather"][0]["description"],
                "wind_speed": data["wind"]["speed"],
                "humidity": data["main"]["humidity"],
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            print(f"❌ Error fetching weather: {e}")
            return self._get_mock_weather(location)
    
    def get_weather_forecast(self, location: str, days: int = 5) -> List[Dict[str, Any]]:
        """Get weather forecast for next N days."""
        if self.mock_mode:
            return self._get_mock_forecast(location, days)
        
        try:
            city = location.split(",")[0].strip()
            
            url = f"{self.base_url}/forecast"
            params = {
                "q": city,
                "appid": self.api_key,
                "units": "metric",
                "cnt": days * 8  # 8 forecasts per day (3-hour intervals)
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # Group by day and find max severity
            forecasts = []
            for item in data["list"][::8]:  # One per day
                forecasts.append({
                    "date": item["dt_txt"].split()[0],
                    "temperature": item["main"]["temp"],
                    "condition": item["weather"][0]["main"],
                    "description": item["weather"][0]["description"],
                    "wind_speed": item["wind"]["speed"]
                })
            
            return forecasts
        except Exception as e:
            print(f"❌ Error fetching forecast: {e}")
            return self._get_mock_forecast(location, days)
    
    def assess_logistics_risk(self, location: str) -> Dict[str, Any]:
        """Assess weather-related logistics risks for a location."""
        weather = self.get_current_weather(location)
        forecast = self.get_weather_forecast(location, days=7)
        
        risk_level = "Low"
        risk_factors = []
        delay_estimate = 0
        
        # Analyze current conditions
        condition = weather.get("condition", "").lower()
        wind_speed = weather.get("wind_speed", 0)
        
        if condition in ["thunderstorm", "tornado", "hurricane"]:
            risk_level = "High"
            risk_factors.append(f"Severe weather: {weather.get('description')}")
            delay_estimate += 3
        elif condition in ["rain", "snow", "drizzle"] and wind_speed > 10:
            risk_level = "Medium"
            risk_factors.append(f"Adverse conditions: {weather.get('description')}")
            delay_estimate += 1
        elif wind_speed > 15:
            risk_level = "Medium"
            risk_factors.append(f"High winds: {wind_speed} m/s")
            delay_estimate += 1
        
        # Check forecast
        for day_forecast in forecast:
            day_condition = day_forecast.get("condition", "").lower()
            if day_condition in ["thunderstorm", "snow", "hurricane"]:
                risk_factors.append(f"Upcoming: {day_forecast['description']} on {day_forecast['date']}")
                delay_estimate += 2
                if risk_level == "Low":
                    risk_level = "Medium"
        
        return {
            "location": location,
            "risk_level": risk_level,
            "delay_estimate_days": delay_estimate,
            "risk_factors": risk_factors,
            "current_weather": weather,
            "assessed_at": datetime.utcnow().isoformat()
        }
    
    def _get_mock_weather(self, location: str) -> Dict[str, Any]:
        """Return mock weather data for testing."""
        mock_conditions = {
            "Mumbai": {"temp": 32, "condition": "Clear", "desc": "clear sky", "wind": 5},
            "Kochi": {"temp": 28, "condition": "Rain", "desc": "heavy intensity rain", "wind": 12},
            "Ho Chi Minh": {"temp": 30, "condition": "Clouds", "desc": "scattered clouds", "wind": 7},
            "California": {"temp": 22, "condition": "Clear", "desc": "clear sky", "wind": 4},
            "Florida": {"temp": 27, "condition": "Thunderstorm", "desc": "thunderstorm", "wind": 18},
            "Texas": {"temp": 35, "condition": "Clear", "desc": "extreme heat", "wind": 8},
        }
        
        # Find matching location
        for key, data in mock_conditions.items():
            if key.lower() in location.lower():
                return {
                    "location": location,
                    "temperature": data["temp"],
                    "condition": data["condition"],
                    "description": data["desc"],
                    "wind_speed": data["wind"],
                    "humidity": 65,
                    "timestamp": datetime.utcnow().isoformat()
                }
        
        # Default
        return {
            "location": location,
            "temperature": 25,
            "condition": "Clear",
            "description": "clear sky",
            "wind_speed": 5,
            "humidity": 60,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def _get_mock_forecast(self, location: str, days: int) -> List[Dict[str, Any]]:
        """Return mock forecast data."""
        forecasts = []
        base_date = datetime.utcnow()
        
        for i in range(days):
            date = base_date + timedelta(days=i)
            forecasts.append({
                "date": date.strftime("%Y-%m-%d"),
                "temperature": 25 + (i % 5),
                "condition": "Clear" if i % 3 != 0 else "Rain",
                "description": "clear sky" if i % 3 != 0 else "light rain",
                "wind_speed": 5 + (i % 3)
            })
        
        return forecasts


class NewsAndTrendsService:
    """Integrates with news APIs for market trends and supply chain events."""
    
    def __init__(self, api_key: str = None):
        """Initialize news service."""
        self.api_key = api_key or os.getenv("NEWS_API_KEY")
        self.mock_mode = not self.api_key
        
        if self.mock_mode:
            print("⚠️ Warning: NEWS_API_KEY not set. Using mock data.")
    
    def get_supply_chain_news(self, keywords: List[str] = None) -> List[Dict[str, Any]]:
        """Fetch recent news about supply chain disruptions."""
        if keywords is None:
            keywords = ["supply chain", "port strike", "shipping delay", "logistics"]
        
        if self.mock_mode:
            return self._get_mock_news()
        
        try:
            url = "https://newsapi.org/v2/everything"
            params = {
                "q": " OR ".join(keywords),
                "apiKey": self.api_key,
                "language": "en",
                "sortBy": "publishedAt",
                "pageSize": 10
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            return [
                {
                    "title": article["title"],
                    "description": article.get("description", ""),
                    "source": article["source"]["name"],
                    "published_at": article["publishedAt"],
                    "url": article["url"]
                }
                for article in data.get("articles", [])
            ]
        except Exception as e:
            print(f"❌ Error fetching news: {e}")
            return self._get_mock_news()
    
    def get_product_trends(self, category: str = "electronics") -> List[Dict[str, Any]]:
        """Get trending products in a category."""
        if self.mock_mode:
            return self._get_mock_trends(category)
        
        # In production, this could integrate with Google Trends API or similar
        return self._get_mock_trends(category)
    
    def _get_mock_news(self) -> List[Dict[str, Any]]:
        """Return mock news data."""
        return [
            {
                "title": "Cyclone Approaching Indian West Coast - Port Operations Suspended",
                "description": "Major ports in Mumbai and Kochi suspend operations due to severe cyclone warning.",
                "source": "Global Logistics News",
                "published_at": datetime.utcnow().isoformat(),
                "url": "https://example.com/news1"
            },
            {
                "title": "Semiconductor Demand Surges in Q4 2025",
                "description": "AI chip manufacturers report record orders, leading to supply constraints.",
                "source": "Tech Industry Today",
                "published_at": (datetime.utcnow() - timedelta(days=1)).isoformat(),
                "url": "https://example.com/news2"
            },
            {
                "title": "Port Workers Strike in Southeast Asia Ports",
                "description": "Labor disputes cause delays in Ho Chi Minh City and Bangkok shipping hubs.",
                "source": "Maritime News",
                "published_at": (datetime.utcnow() - timedelta(days=2)).isoformat(),
                "url": "https://example.com/news3"
            }
        ]
    
    def _get_mock_trends(self, category: str) -> List[Dict[str, Any]]:
        """Return mock trend data."""
        return [
            {
                "product": "AI-Enhanced IoT Sensors",
                "trend_score": 92,
                "growth_rate": "+45%",
                "reasoning": "Growing demand for smart home and industrial IoT applications"
            },
            {
                "product": "Energy-Efficient Power Modules",
                "trend_score": 87,
                "growth_rate": "+38%",
                "reasoning": "Increased focus on sustainable electronics and green energy"
            },
            {
                "product": "5G Communication Chips",
                "trend_score": 84,
                "growth_rate": "+32%",
                "reasoning": "5G infrastructure expansion in emerging markets"
            }
        ]


# Singleton instances
_weather_service = None
_news_service = None

def get_weather_service():
    """Get or create weather service singleton."""
    global _weather_service
    if _weather_service is None:
        _weather_service = WeatherService()
    return _weather_service

def get_news_service():
    """Get or create news service singleton."""
    global _news_service
    if _news_service is None:
        _news_service = NewsAndTrendsService()
    return _news_service
