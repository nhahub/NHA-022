import streamlit as st
from db import Cassandra
import matplotlib.pyplot as plt

@st.cache_resource
def get_cassandra():
  return Cassandra()

cassandra = get_cassandra()
cassandra.exec("SELECT * FROM crack")
data = cassandra.join_roads()

st.title("Pavement eye")


st.markdown("###### Data")
st.dataframe(data)

# ----------------------------------------------------------------------------------
fig, ax = plt.subplots(1, 1)

plot = data.groupby('label')['id'].count()
ax.pie(plot, labels=plot.index, autopct='%.2f%%')
st.pyplot(fig)
