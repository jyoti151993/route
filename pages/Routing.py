import streamlit as st
import pandas as pd
from streamlit_folium import st_folium
from helper import *


st.set_page_config(
    layout="wide"
)

data = get_data()

location_list = data['id'].to_list()

cc1, cc2, cc3, cc4, cc5 = st.columns([1, 7, 1, 7, 1])

with cc2:
    st.text('')
    st.text('')
    ch = st.selectbox('Choose Start Point ', location_list)
    st.text('')
    st.text('')
location_list_2 = [x for x in location_list if x != ch]
with cc4:
    st.text('')
    st.text('')
    ch1 = st.selectbox('Choose End Point', location_list_2)
    st.text('')
    st.text('')

c1, c2, c3 = st.columns([1, 8, 1])
with c2:
    st.header("Shortest Route by Distance Vs Time")
    map_, stats1, stats2 = shortest_length_map(data, ch, ch1)
    st.write(stats1)
    st.write(stats2)
    st_data = st_folium(map_, width=1300, height=750)
