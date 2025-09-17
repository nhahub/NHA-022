import streamlit as st
import pydeck as pdk
from db import Cassandra

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