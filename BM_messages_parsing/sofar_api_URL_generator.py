# filename: sofar_api_URL_generator.py
# description: define the API url call based on SPOT ID, API Token, and dates of interest


# Specify Spotter ID
#spotterId = "SPOT-31380C" # Camera Module
#spotterId = "SPOT-31088C" # HMB Unit
spotterId = "SPOT-32071C" # dockside camera
#spotterId = "SPOT-32071C" # HMB hydrophone test unit
#spotterId = "SPOT-32010C" # IMU prototype

# API tokens
#token = "90bda8b0a39b9570b548ab6f7a1aea" # sofar eng key
token = "019058d08091ed2b1f96e774344874" # nick's admin key


# Dates for searching
start_date = "2024-12-06T00:00:00Z"
end_date = "2024-12-08T00:00:00Z"


# =======================
# For Spotter Wave data
# =======================

# URL for "latest" data
api_url_latest = f"https://api.sofarocean.com/api/latest-data?spotterId={spotterId}&token={token}"
print("Spotter wave URL for latest data")
print(api_url_latest)

# URL for "latest" data with extras
api_url_latest_extras = f"https://api.sofarocean.com/api/latest-data?spotterId={spotterId}&token={token}&includeWindData=true&includeSurfaceTempData=true&includeBarometerData=true"
print("Spotter wave URL for latest data with extras")
print(api_url_latest_extras)

# URL with end dates
api_url_with_dates = f"https://api.sofarocean.com/api/wave-data?spotterId={spotterId}&startDate={start_date}&endDate={end_date}&token={token}&includeWindData=true&includeSurfaceTempData=true&includeBarometerData=true"
print("Spotter wave URL with dates")
print(api_url_with_dates)

# URL with
api_url = f"https://api.sofarocean.com/api/wave-data?spotterId={spotterId}&limit=100&startDate={start_date}&endDate={end_date}&token={token}"
print("Spotter wave URL simple")
print(api_url)

# URL with
api_url = f"https://api.sofarocean.com/api/wave-data?spotterId={spotterId}&limit=100&token={token}"
print("Spotter wave no start or end URL simple")
print(api_url)

# =======================
# For Smart Mooring data
# =======================

# URL with end dates
api_url_with_dates = f"https://api.sofarocean.com/api/sensor-data?spotterId={spotterId}&startDate={start_date}&endDate={end_date}&token={token}"
print("Smart mooring URL with dates")
print(api_url_with_dates)

# URL with
api_url = f"https://api.sofarocean.com/api/sensor-data?spotterId={spotterId}&startDate={start_date}&endDate={end_date}&token={token}"
print("Smart mooring URL simple")
print(api_url)
