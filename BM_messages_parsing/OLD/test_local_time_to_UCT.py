from datetime import datetime
import pytz

# Input the local timestamp as a string
local_date_str = "2024-11-23T19:37:00"  # Replace with your local date and time
local_timezone_str = "America/Los_Angeles"  # Replace with your local timezone

# Parse the local timestamp
local_timezone = pytz.timezone(local_timezone_str)
local_datetime = local_timezone.localize(datetime.strptime(local_date_str, "%Y-%m-%dT%H:%M:%S"))

# Convert to UTC
utc_datetime = local_datetime.astimezone(pytz.utc)
deployment_date_str = utc_datetime.strftime("%Y-%m-%dT%H:%M:%SZ")

print(f"Local Time: {local_datetime}")
print(f"UTC Time: {deployment_date_str}")
