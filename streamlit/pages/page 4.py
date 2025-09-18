import streamlit as st
from db import Cassandra
import pandas as pd
import matplotlib.pyplot as plt

cassandra = Cassandra()
cassandra.exec("SELECT x1,x2,y1,y2, road_index, label, ppm, timestamp FROM crack")
cassandra.join_roads()
cassandra.calc_pci()
data = cassandra.data

data = data.to_crs(epsg=3857)

data = data.sort_values("timestamp")
data = data.set_index("timestamp")

monthly_pci = data["pci"].resample("ME").mean().fillna(method='ffill')

rolling_pci = monthly_pci.rolling(window=3).mean().fillna(method='ffill')

print(monthly_pci)
print(rolling_pci)

fig, ax = plt.subplots(figsize=(10, 5))  # Create figure and axis

ax.plot(monthly_pci.index, monthly_pci, label="Monthly PCI")
ax.plot(rolling_pci.index, rolling_pci, label="3-Month Rolling Avg", linewidth=3)

ax.set_xlabel("Date")
ax.set_ylabel("PCI")
ax.set_title("Monthly PCI with Rolling Average")
ax.legend()
ax.grid(True)

st.pyplot(fig)
