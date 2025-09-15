import streamlit as st
from db import Cassandra

@st.cache_resource
def get_cassandra():
  return Cassandra()

cassandra = get_cassandra()
data = cassandra.exec("SELECT * FROM crack")
st.dataframe(data)

