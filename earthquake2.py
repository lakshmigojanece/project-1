import requests
import pandas 
from sqlalchemy import create_engine
url = "https://earthquake.usgs.gov/fdsnws/event/1/query"
earthquake = []
# Fixed years: 2020 → 2025 
start_year = 2020 
end_year = 2025
for year in range(start_year, end_year + 1):
    for month in range(1, 13):

        start_date = f"{year}-{month:02d}-01"

        if month == 12:
            end_date = f"{year + 1}-01-01"
        else:
            end_date = f"{year}-{month + 1:02d}-01"

        print(f"Fetching {start_date} → {end_date}")

        params = {
            "format": "geojson",
            "starttime": start_date,
            "endtime": end_date,
            "minmagnitude": 3,
            "limit": 20000    # max allowed by USGS
        }

        try:
            response = requests.get(url, params=params)
            data = response.json()
        except Exception:
            print(" JSON decode error. Response:")
            print(response.text[:500])
            continue  # skip to next month


        
        events = data.get("features", [])

        for eq in events:
            props = eq["properties"]
            geo = eq["geometry"]

            earthquake.append({
                "id": eq.get("id"),
                "time": props.get("time"),
                "updated": props.get("updated"),
                "latitude": geo["coordinates"][1],
                "longitude": geo["coordinates"][0],
                "depth_km": geo["coordinates"][2],
                "mag": props.get("mag"),
                "magType": props.get("magType"),
                "place": props.get("place"),
                "status": props.get("status"),
                "tsunami": props.get("tsunami"),
                "sig": props.get("sig"),
                "net": props.get("net"),
                "nst": props.get("nst"),
                "dmin": props.get("dmin"),
                "rms": props.get("rms"),
                "gap": props.get("gap"),
                "magError": props.get("magError"),
                "depthError": props.get("depthError"),
                "magNst": props.get("magNst"),
                "locationsource": props.get("locationSource"),
                "magsource": props.get("magSource"),
                "types": props.get("types"),
                "ids": props.get("ids"),
                "sources": props.get("sources"),
                "type": props.get("type")
            })

# Convert to DataFrame
df = pd.DataFrame(earthquake)

# Convert timestamps (milliseconds → datetime)
df["time"] = pd.to_datetime(df["time"], unit="ms")
df["updated"] = pd.to_datetime(df["updated"], unit="ms")
print("--------------------------------------------")

print(df.head())


HOST = "localhost"
USER = "root"
PASSWORD = "root"      # change this
DATABASE = "earthquakes_py"

engine = create_engine(f"mysql+pymysql://{root}:{root}@{localhost}/{earthquakes_py}")

df.to_sql("earthquake_data", con=engine, if_exists="append", index=False)

print("Data inserted successfully into MySQL!")

