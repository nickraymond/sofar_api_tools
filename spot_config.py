# spot_config.py

from datetime import datetime

# List of dictionaries, each containing a SPOT ID and its corresponding start and end dates
SPOTTER_CONFIGS = [
    {
        'spotter_id': 'SPOT-31088C', ## HMB unit w/current meter
        'start_date': datetime(2025, 1, 28), # 2024-10-31 real date
        'end_date': datetime.utcnow()
    },
    # {
    #     'spotter_id': 'SPOT-30022R', # HMB reference spar buoy
    #     'start_date': datetime(2024, 8, 20),
    #     'end_date': datetime(2024, 11, 20)
    # },
    # Add more configurations as needed
]
