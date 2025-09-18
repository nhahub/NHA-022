import streamlit as st
import matplotlib.pyplot as plt
from db import Cassandra
import plotly.express as px
import pandas as pd

st.title("Percentage of each crack type for different road types")
st.markdown("""
Normal road means road that is not tunnel or bridge.
""")

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

# ----------------------------------------------------------------------------------------
st.markdown("""
#### Percentage of each crack type for different road types (Tables)
""")

st.markdown("""
###### Brige
""")
st.dataframe(bridge)

st.markdown("""
###### Tunnel
""")
st.dataframe(tunnel)

st.markdown("""
###### Normal
""")
st.dataframe(normal)
# ----------------------------------------------------------------------------------------
cassandra.exec("SELECT x1,x2,y1,y2, road_index, label, ppm FROM crack")
cassandra.join_roads()
cassandra.calc_pci()
df = cassandra.data

df = df[df['road_index'] != -1]

group = df.groupby(['road_index']).agg({
  'name': 'first',
  'pci': 'mean',
  'fclass': 'first'
}).reset_index()

group['name'].fillna(group['road_index'], inplace=True)

group = group.sort_values(by='pci', ascending=False)

top_10_damaged_roads = group['road_index'].to_list()[:10]

fig = px.bar(
    group,
    x='name',
    y='pci',
    hover_data=['name', 'pci', 'fclass'],
    labels={'name': 'Street (road_index)', 'pci': 'PCI', 'fclass': 'Road Type'},
    title='Top 10 damaged streets (based on PCI)'
)

fig.update_layout(
    xaxis_tickangle=-45,
    height=600
)

st.plotly_chart(fig, use_container_width=True)
# -----------------------------------------------------------------------------------------
top_damaged_df = df[df['road_index'].isin(top_10_damaged_roads)]

# Step 1: Replace missing names
top_damaged_df['name'] = top_damaged_df['name'].fillna(top_damaged_df['road_index'])

# Step 2: Create the pivot for counts only
pv = pd.pivot_table(
    top_damaged_df,
    index=['road_index', 'name'],    # include name in index
    columns='label',
    values='geometry',
    aggfunc='count'
).fillna(0).astype(int)

# Step 3: Reset index to flatten
pv_reset = pv.reset_index()   # now includes road_index and name as columns

# Step 4: Melt to long-form
pv_long = pv_reset.melt(
    id_vars=['road_index', 'name'],
    var_name='Crack Type',
    value_name='Count'
)

crack_colors = {
    "Alligator Crack": "#e6194b",      # red
    "Transverse Crack": "#3cb44b",     # green
    "Longitudinal Crack": "#ffe119",   # yellow
    "Pothole": "#4363d8",              # blue
}

# Step 5: Plot using road name as x-axis
fig = px.bar(
    pv_long,
    x='name',
    y='Count',
    color='Crack Type',
    color_discrete_map=crack_colors,  # ← here
    title='Crack Types for the top 10 damaged roads',
    labels={'name': 'Road Name (road_index)', 'Count': 'Number of Cracks'},
)

fig.update_layout(
    barmode='stack',
    xaxis_tickangle=-45,
    xaxis={'type': 'category'}
)

st.plotly_chart(fig, use_container_width=True)

