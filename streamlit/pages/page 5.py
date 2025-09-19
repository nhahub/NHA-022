import streamlit as st
from db import Cassandra
import matplotlib.pyplot as plt
import plotly.graph_objects as go

# Global styles -------------------------------------------------------------------
st.set_page_config(layout="wide")

# Load the external CSS file
def local_css(file_name):
  with open(file_name) as f:
      st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

local_css("./style.css")

cmap = plt.get_cmap('Dark2')
# ---------------------------------------------------------------------------------

cassandra = Cassandra()
cassandra.exec("SELECT label, road_index FROM crack")
cassandra.join_roads()
cracks_df = cassandra.data

col1, col2 = st.columns([2, 1])

with col1:

  st.markdown("##### Comparison between different road speeds")

  cracks_df = cracks_df[cracks_df['maxspeed'] > 0]

  speed_cracks = (
      cracks_df.groupby(["maxspeed", "label"])
      .size()
      .reset_index(name="count")
  )

  pivot_speed = speed_cracks.pivot(
      index="maxspeed", columns="label", values="count"
  ).fillna(0)

  pivot_percent = pivot_speed.div(pivot_speed.sum(axis=1), axis=0) * 100

  pivot_percent = pivot_percent.sort_index()

  fig, ax = plt.subplots(1, 1)
  pivot_percent.plot(
      kind="bar",
      stacked=True,
      figsize=(12,6),
      ax=ax,
      colormap=cmap
  )

  # Corrected annotation loop
  counts = cracks_df\
    .groupby(['maxspeed'])\
    .size()\
    .sort_index()\
    .to_list()

  for i, count in enumerate(counts):
    # Use the integer index `i` for the x-coordinate
    ax.annotate(f"{count} cracks", xy=(i, 100), ha='center', va='bottom', fontsize=15)

  ax.set_title("Percentage of Crack Types per Maxspeed", fontsize=14, fontweight="bold")
  ax.set_xlabel("Maxspeed in KM/H", fontsize=12)
  ax.set_ylabel("Percentage (%)", fontsize=12)
  ax.legend(title="Crack Type")
  ax.grid(axis="y", linestyle="--", alpha=0.7)
  st.pyplot(fig)
# ------------------------------------------------------------------------------------------

with col2:
  st.markdown("##### One way roads vs both")
  df = cassandra.data

  oneway_B = df[df['oneway'] == 'B'].groupby(['label']).size()
  oneway_F = df[df['oneway'] == 'F'].groupby(['label']).size()

  categories_B = df[df['oneway'] == 'B']['label'].unique()
  categories_F = df[df['oneway'] == 'F']['label'].unique()

  fig = go.Figure()

  fig.add_trace(go.Scatterpolar(
        r=oneway_B.values,
        theta=categories_B,
        fill='toself',
        name='Both',
  ))
  fig.add_trace(go.Scatterpolar(
        r=oneway_F.values,
        theta=categories_F,
        fill='toself',
        name='False'
  ))


  fig.update_layout(
    polar=dict(
      radialaxis=dict(
        visible=True,
        range=[0, 5]
      )),
    showlegend=False
  )

  st.plotly_chart(fig, use_container_width=True)
# -------------------------------------------------------------------------------------

