import streamlit as st
from helper import *
from streamlit_folium import st_folium
import base64

st.set_page_config(
    page_title="Welcome to SIngapore Routing",
    layout="wide"
)


def get_base64(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()


def set_background(png_file):
    bin_str = get_base64(png_file)
    page_bg_img = '''
    <style>
    .stApp {
    background-image: url("data:image/png;base64,%s");
    background-size: cover;
    }
    </style>
    ''' % bin_str
    st.markdown(page_bg_img, unsafe_allow_html=True)


set_background(r"sing.png")

dtf = get_data()
start = dtf[["y", "x"]].values[0]

c1, c2 = st.columns([1, 3], gap='medium')
with c1:
    st.write("")
    st.write("")
    st.write("")
    st.write("")
    st.write("")
    st.write("")
    st.write("")
    st.write("")
    st.write("")
    st.write("")
    st.write("")
    st.write("")
    st.write("")
    st.write("")
    st.write("")
    st.write("")
    st.markdown(
        f"<h5 style='text-align: center; letter-spacing:2px;font-size: 30px; color: #ADD8E6;'><span "f"style"f"='font"
        f"-size: 40px;'> MapUp || Route Optimization Tool",
        unsafe_allow_html=True)

with c2:
    map_ = plot_map(dtf, y="y", x="x", start=start, zoom=11,
                    tiles="cartodbpositron", popup="id", lst_colors=["black", "red"])
    st.data = st_folium(map_, width=1500, height=750)
st.sidebar.success("Select routing to plot a route between two points")
