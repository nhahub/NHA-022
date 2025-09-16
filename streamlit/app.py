import streamlit as st
from db import Cassandra

@st.cache_resource
def get_cassandra():
  return Cassandra()

cassandra = get_cassandra()
cassandra.exec("SELECT * FROM crack")
data = cassandra.join_roads()

st.title("Pavement eye")

st.markdown("###### Data")
st.dataframe(data)

