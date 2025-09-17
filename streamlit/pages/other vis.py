import streamlit as st
import matplotlib.pyplot as plt
from db import Cassandra

cassandra = Cassandra()
cassandra.exec("SELECT road_index, label FROM crack")
df = cassandra.join_roads()

bridge = df[df['bridge'] == 'T'].groupby(['label']).size()
tunnel = df[df['tunnel'] == 'T'].groupby(['label']).size()

normal = df[(df['bridge'] == 'F') & (df['bridge'] == 'F')].groupby(['label']).size()

fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(12, 4))
ax1.pie(bridge, labels=bridge.index, autopct='%0.2f%%')
ax1.set_title("bridge")
ax2.pie(tunnel, labels=tunnel.index, autopct='%0.2f%%')
ax2.set_title("tunnel")
ax3.pie(normal, labels=normal.index, autopct='%0.2f%%')
ax3.set_title("normal")
st.pyplot(fig)

st.dataframe(bridge)
st.dataframe(tunnel)
st.dataframe(normal)