# # Simple script to show a map of san francisco in HTML
#
# import folium
#
# # Replace with your Mapbox access token
# mapbox_access_token = 'pk.eyJ1Ijoibmlja3JheW1vbmQ5OSIsImEiOiJjbHlrdDYzMmExM3psMm1vam92c2c4NjB3In0.1KVs_Kh_128z249Iqz5g0Q'
#
# # Create a map centered on San Francisco
# sf_map = folium.Map(
#     location=[37.7749, -122.4194],
#     zoom_start=12,
#     tiles=f"https://api.mapbox.com/styles/v1/mapbox/streets-v11/tiles/{{z}}/{{x}}/{{y}}?access_token={mapbox_access_token}",
#     attr="Mapbox",
# )
#
# # Add a marker for San Francisco
# folium.Marker([37.7749, -122.4194], popup="San Francisco").add_to(sf_map)
#
# # Save the map to an HTML file
# sf_map.save("san_francisco_map.html")
#
# print("Map saved to san_francisco_map.html")

import pandas as pd
import plotly.express as px

# Replace with your Mapbox Access Token
mapbox_access_token = 'pk.eyJ1Ijoibmlja3JheW1vbmQ5OSIsImEiOiJjbHlrdDYzMmExM3psMm1vam92c2c4NjB3In0.1KVs_Kh_128z249Iqz5g0Q'

# Sample GPS data: Golden Gate Bridge to Alcatraz Island
gps_data = {
    "latitude": [37.8199, 37.8210, 37.8221, 37.8250, 37.8265],
    "longitude": [-122.4783, -122.4700, -122.4600, -122.4500, -122.4230],
    "timestamp": [
        "2023-11-19T12:00:00Z",
        "2023-11-19T12:10:00Z",
        "2023-11-19T12:20:00Z",
        "2023-11-19T12:30:00Z",
        "2023-11-19T12:40:00Z",
    ],
}

# Convert data to DataFrame
gps_df = pd.DataFrame(gps_data)
gps_df['timestamp'] = pd.to_datetime(gps_df['timestamp'])  # Convert to datetime for slider

# Create an interactive map with Plotly
fig = px.scatter_mapbox(
    gps_df,
    lat="latitude",
    lon="longitude",
    color="timestamp",
    size_max=10,
    zoom=13,
    center={"lat": gps_df['latitude'].mean(), "lon": gps_df['longitude'].mean()},
    animation_frame="timestamp",  # Add a time slider
    title="GPS Path: Golden Gate Bridge to Alcatraz Island",
)

# Configure Mapbox
fig.update_layout(
    mapbox_style="mapbox://styles/mapbox/streets-v11",
    mapbox_accesstoken=mapbox_access_token,
    margin={"r": 0, "t": 50, "l": 0, "b": 0},
)

# Save the interactive map to an HTML file
html_file = "golden_gate_to_alcatraz.html"
fig.write_html(html_file)
print(f"Interactive map saved to {html_file}. Open it in your browser to view.")
