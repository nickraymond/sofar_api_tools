import os
from datetime import datetime, timedelta

# API Configuration
API_TOKEN = "019058d08091ed2b1f96e774344874"

# Spotter Configuration
SPOTTER_ID = "SPOT-31088C" # HMB with load cell
#SPOTTER_ID = "SPOT-32071C" # HMB hydrophone test unit
# Deployment date as a string
DEPLOYMENT_DATE_STR = "2024-11-24T00:00:00Z"

# SPOTTER_ID = "SPOT-32010C" # IMU prototype
# DEPLOYMENT_DATE_STR = "2024-12-06T00:00:00Z"

# Time range for data fetching
DAYS_AFTER = 1  # How many days after the deployment to fetch data

# Parse deployment date into a datetime object
DEPLOYMENT_DATE = datetime.strptime(DEPLOYMENT_DATE_STR, "%Y-%m-%dT%H:%M:%SZ")

# Calculate START_DATE and END_DATE
START_DATE = DEPLOYMENT_DATE
END_DATE = DEPLOYMENT_DATE + timedelta(days=DAYS_AFTER)

print(f"Start Date: {START_DATE}")
print(f"End Date: {END_DATE}")

# Conversion factors
METER_TO_FEET = 3.28084
M_PER_S_TO_KNOTS = 1.94384
NEWTON_TO_LBF = 0.224809
