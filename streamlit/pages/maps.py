import streamlit as st
from streamlit_keplergl import keplergl_static
from app import data

from keplergl import KeplerGl


# Create a KeplerGl map instance
map_1 = KeplerGl(height=600)

# Add your data as a layer named "my_data"
map_1.add_data(data=data)

# Render map inside Streamlit
kepler_map = keplergl_static(map_1)