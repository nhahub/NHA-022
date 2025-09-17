import streamlit as st
from db import Cassandra
import matplotlib.pyplot as plt
import plotly.express as px

cassandra = Cassandra()
cassandra.exec("SELECT * FROM crack LIMIT 10")
data = cassandra.join_roads()
data = data.drop(['geometry'], axis=1)

st.title("Pavement eye")


st.markdown("###### Last 10 cracks")
st.dataframe(data)

# ----------------------------------------------------------------------------------
data1 = cassandra.exec("SELECT label FROM crack")

fig, ax = plt.subplots(1, 1)

plot = data1.groupby('label')['label'].count()
ax.pie(plot, labels=plot.index, autopct='%.2f%%')
st.pyplot(fig)
# -----------------------------------------------------------------------------------
cassandra.exec("SELECT road_index, label FROM crack")
data2 = cassandra.join_roads()

grouped_df = data2.groupby(["fclass", "label"]).size().reset_index(name='count')

# Title
st.title("Crack Type by Road Type Treemap")

# Treemap plot
fig = px.treemap(
  grouped_df,
  path=["fclass", "label"],
  values="count",
  color="fclass",
  title="Distribution of Crack Types Across Road Types"
)

st.plotly_chart(fig, use_container_width=True)
# ----------------------------------------------------------------------------------
data2 = data2.to_crs("EPSG:3857")
data2['length_km'] = data2.geometry.length / 1000
total_len_km = data2['length_km'].sum()

st.markdown(f"""
### Total Number of cracks = {len(data2)}


### Total length in Km = {total_len_km}
""")