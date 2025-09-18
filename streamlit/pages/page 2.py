import streamlit as st
import pydeck as pdk
from db import Cassandra
import json
import matplotlib.pyplot as plt
import contextily as ctx

cassandra = Cassandra()
cassandra.exec("SELECT lon, lat, confidence FROM crack")
data = cassandra.data

st.title("Cracks heatmap")

view_state = pdk\
.ViewState(
    latitude=data['lat'].iloc[0], 
    longitude=data['lon'].iloc[0], 
    zoom=10, 
    pitch=45
)

layer = pdk.Layer(
    "HeatmapLayer",
    data=data,
    get_position=["lon", "lat"],
    get_weight='confidence',  # Weight by confidence
    aggregation="MEAN",
    radiusPixels=60,  # Smaller heatmap radius
    intensity=1.2,    # Lower intensity
    colorRange=[
        [46, 204, 113, 80],        # Emerald Green (low density) - more transparent
        [241, 196, 15, 120],       # Sunflower Yellow
        [230, 126, 34, 160],       # Carrot Orange  
        [231, 76, 60, 200],        # Alizarin Red (high density)
    ],
    pickable=False,
)

deck = pdk.Deck(
    layers=[layer],
    initial_view_state=view_state,
)
st.pydeck_chart(deck)
# -----------------------------------------------------------------------------------------------
st.title("Roads PCI")

cassandra.exec("SELECT x1,x2,y1,y2, road_index, label, ppm FROM crack")
cassandra.join_roads()
cassandra.calc_pci()
data = cassandra.data

data["color"] = data["condition"].map({
    "Excellent": [0, 255, 0],        # Bright neon green
    "Good": [0, 200, 255],           # Cyan / bright sky blue
    "Fair": [255, 255, 0],           # Pure yellow
    "Poor": [255, 165, 0],           # Bright orange
    "Very Poor": [255, 0, 255],      # Magenta (very visible)
    "Failed": [255, 0, 0],           # Bright red
})

geojson_data = json.loads(data.to_json())

tooltip = {
    "html": """
        <b>Street:</b> {name}<br>
        <b>Condition:</b> {condition}<br>
        <b>PCI:</b> {pci}<br>
        <b>Crack Type:</b> {label}
    """,
    "style": {
        "backgroundColor": "steelblue",
        "color": "white",
        "fontSize": "12px"
    }
}

# 2. Create Pydeck Layer
layer = pdk.Layer(
    "GeoJsonLayer",
    data=geojson_data,  # must be a dict or URL
    get_line_color="properties.color",  # must be stored in properties
    get_line_width=7,
    pickable=True,
    auto_highlight=True
)

# 3. Define view
view_state = pdk.ViewState(
    latitude=data.geometry.centroid.y.mean(),
    longitude=data.geometry.centroid.x.mean(),
    zoom=12
)

# 4. Render
deck = pdk.Deck(layers=[layer], initial_view_state=view_state, tooltip=tooltip, map_style="light")
st.pydeck_chart(deck)
# --------------------------------------------------------------------------------------------------
# data = data.to_crs(epsg=3857)
# data.plot(label='condition')

# fig, ax = plt.subplots(figsize=(10, 10))
# data.plot(ax=ax, linewidth=3, color='green')
# ctx.add_basemap(ax)
# ax.set_axis_off()
# plt.tight_layout()
# st.pyplot(fig)