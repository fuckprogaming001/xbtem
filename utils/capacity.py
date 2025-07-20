from datetime import datetime, timedelta
import pytz  # type: ignore

# This list defines the capacity and pricing for different countries.
capacity_collections = [
    {
        "country": "BD",
        "price": 0.25,
        "country_code": "+880",
        "capacity": 100,
        "unlock_time": datetime.now(pytz.utc) + timedelta(minutes=59),
        "country_imogi": "🇧🇩"
    },
    {
        "country": "CO",
        "price": 0.30,
        "country_code": "+57",
        "capacity": 100,
        "unlock_time": datetime.now(pytz.utc) + timedelta(minutes=59),
        "country_imogi": "🇨🇴"
    },
    {
        "country": "USA",
        "country_code": "+1",
        "price": 0.21,
        "capacity": 1,
        "unlock_time": datetime.now(pytz.utc) + timedelta(hours=59),
        "country_imogi": "🇺🇸"
    },
    {
        "country": "Algeria",
        "country_code": "+213",
        "price": 0.40,
        "capacity": 100,
        "unlock_time": datetime.now(pytz.utc) + timedelta(hours=59),
        "country_imogi": "🇩🇿"
    },
    {
        "country": "India",
        "country_code": "+91",
        "price": 0.50,
        "capacity": 100,
        "unlock_time": datetime.now(pytz.utc) + timedelta(hours=59),
        "country_imogi": "🇮🇳"
    },
    {
        "country": "UK",
        "country_code": "+44",
        "price": 1,
        "capacity": 100,
        "unlock_time": datetime.now(pytz.utc) + timedelta(hours=59),
        "country_imogi": "🇬🇧"
    }
]
