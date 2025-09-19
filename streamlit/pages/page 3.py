import streamlit as st
import matplotlib.pyplot as plt
from db import Cassandra
import plotly.express as px
import pandas as pd
import numpy as np

# Global styles -------------------------------------------------------------------
st.set_page_config(layout="wide")

# Load the external CSS file
def local_css(file_name):
  with open(file_name) as f:
      st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

local_css("./style.css")

cmap = plt.get_cmap('Dark2')
# ---------------------------------------------------------------------------------

st.title("Percentage of each crack type for different road types")
st.markdown("""
Normal road means road that is not tunnel or bridge.
""")

cassandra = Cassandra()
cassandra.exec("SELECT road_index, label FROM crack")
df = cassandra.join_roads()

bridge = df[df['bridge'] == 'T'].groupby(['label']).size().rename('count')
tunnel = df[df['tunnel'] == 'T'].groupby(['label']).size().rename('count')

normal = df[(df['bridge'] == 'F') & (df['bridge'] == 'F')].groupby(['label']).size().rename('count')

colors1 = cmap(np.linspace(0, 1, len(bridge.index)))
colors2 = cmap(np.linspace(0, 1, len(tunnel.index)))
colors3 = cmap(np.linspace(0, 1, len(normal.index)))

fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(12, 4), dpi=200)
ax1.pie(bridge, labels=bridge.index, autopct='%0.2f%%', colors=colors1)
ax1.set_title("bridge")
ax2.pie(tunnel, labels=tunnel.index, autopct='%0.2f%%', colors=colors2)
ax2.set_title("tunnel")
ax3.pie(normal, labels=normal.index, autopct='%0.2f%%', colors=colors3)
ax3.set_title("normal")
st.pyplot(fig)

# ----------------------------------------------------------------------------------------

col1, col2, col3 = st.columns(3)

st.markdown("""
#### Percentage of each crack type for different road types (Tables)
""")

with col1:
    st.markdown("""
    ###### Brige
    """)
    st.dataframe(bridge)

with col2:
    st.markdown("""
    ###### Tunnel
    """)
    st.dataframe(tunnel)

with col3:
    st.markdown("""
    ###### Normal
    """)
    st.dataframe(normal)
# ----------------------------------------------------------------------------------------

col1, col2 = st.columns(2)

with col1:

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
        y='name',
        x='pci',
        hover_data=['name', 'pci', 'fclass'],
        labels={'name': 'Street (road_index)', 'pci': 'PCI', 'fclass': 'Road Type'},
        title='Top 10 damaged streets (based on PCI)',
        color_discrete_sequence=px.colors.qualitative.Dark2
    )

    fig.update_layout(
        height=600
    )

    st.plotly_chart(fig, use_container_width=True)
# -----------------------------------------------------------------------------------------
with col2:
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

    # Step 5: Plot using road name as x-axis
    fig = px.bar(
        pv_long,
        y='name',
        x='Count',
        color='Crack Type',
        color_discrete_sequence=px.colors.qualitative.Dark2,
        title='Crack Types for the top 10 damaged roads',
        labels={'name': 'Road Name (road_index)', 'Count': 'Number of Cracks'},
    )

    fig.update_layout(
        barmode='stack',
        xaxis={'type': 'category'}
    )

    st.plotly_chart(fig, use_container_width=True)
# -----------------------------------------------------------------------------------------
