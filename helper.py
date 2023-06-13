import pandas as pd
import numpy as np
# for plotting
import matplotlib.pyplot as plt  # 3.3.2
import seaborn as sns  # 0.11.1
import folium  # 0.14.0
import streamlit
from folium import plugins
import plotly.express as px  # 5.1.0

# for simple routing
import osmnx as ox  # 1.2.2
import networkx as nx  # 3.0
import pickle
from shapely.wkt import loads
from sklearn import preprocessing

import warnings

warnings.filterwarnings("ignore")




@streamlit.cache_data
def get_data():
    
    #data = pd.read_csv("singapore_taxi.csv")
  with open("singapore_taxi.pkl", "rb") as file:
    data = pickle.load(file)
    return data


'''
Creates a map with folium.
:parameter
    :param dtf: pandas
    :param (y,x): str - columns with (latitude, longitude)
    :param starting_point: list - (latitude, longitude)
    :param tiles: str - "cartodbpositron", "OpenStreetMap", "Stamen Terrain", "Stamen Toner"
    :param popup: str - column with text to popup if clicked, if None there is no popup
    :param size: str - column with size variable, if None takes size=5
    :param color: str - column with color variable, if None takes default color
    :param lst_colors: list - list with multiple colors to use if color column is not None, if not given it generates randomly
    :param marker: str - column with marker variable, takes up to 7 unique values
:return
    map object to display
'''



def plot_map(dtf, y, x, start, zoom=12, tiles="cartodbpositron", popup=None, size=None, color=None, legend=False,
             lst_colors=None, marker=None):
    data = dtf.copy()

    # create columns for plotting
    if color is not None:
        lst_elements = sorted(list(dtf[color].unique()))
        lst_colors = ['#%06X' % np.random.randint(0, 0xFFFFFF) for i in
                      range(len(lst_elements))] if lst_colors is None else lst_colors
        data["color"] = data[color].apply(lambda x: lst_colors[lst_elements.index(x)])

    if size is not None:
        scaler = preprocessing.MinMaxScaler(feature_range=(3, 15))
        data["size"] = scaler.fit_transform(data[size].values.reshape(-1, 1)).reshape(-1)

    # map
    map_ = folium.Map(location=start, tiles=tiles, zoom_start=zoom)

    if (size is not None) and (color is None):
        data.apply(lambda row: folium.Marker(location=[row[y], row[x]], popup=row[popup],
                                             icon=folium.Icon(icon="info-sign", color="purple")).add_to(map_), axis=1)
    elif (size is None) and (color is not None):
        data.apply(lambda row: folium.Marker(location=[row[y], row[x]], popup=row[popup],
                                             icon=folium.Icon(icon="info-sign", color=row["color"])).add_to(map_), axis=1)
    elif (size is not None) and (color is not None):
        data.apply(lambda row: folium.CircleMarker(location=[row[y], row[x]], popup=row[popup],
                                                   color=row["color"], fill=True, radius=row["size"]).add_to(map_),
                   axis=1)
    else:
        data.apply(lambda row: folium.Marker(location=[row[y], row[x]], popup=row[popup],
                                             icon=folium.Icon(icon="info-sign", color="purple")).add_to(map_), axis=1)

    # tiles
    layers = ["cartodbpositron", "openstreetmap", "Stamen Terrain",
              "Stamen Water Color", "Stamen Toner", "cartodbdark_matter"]
    for tile in layers:
        folium.TileLayer(tile).add_to(map_)
    folium.LayerControl(position='bottomright').add_to(map_)

    # legend
    if (color is not None) and (legend is True):
        legend_html = """<div style="position:fixed; bottom:10px; left:10px; border:2px solid black; z-index:9999; 
        font-size:14px;">&nbsp;<b>""" + color + """:</b><br>"""
        for i in lst_elements:
            legend_html = legend_html + """&nbsp;<i class="fa fa-circle fa-1x" style="color:""" + lst_colors[
                lst_elements.index(i)] + """"></i>&nbsp;""" + str(i) + """<br>"""
        legend_html = legend_html + """</div>"""
        map_.get_root().html.add_child(folium.Element(legend_html))

    # add marker
    if marker is not None:
        lst_elements = sorted(list(dtf[marker].unique()))
        lst_colors = ["black", "red", "blue", "green", "pink", "orange", "gray"]  # 7
        # too many values, can't mark
        if len(lst_elements) > len(lst_colors):
            raise Exception("marker has uniques > " + str(len(lst_colors)))
        # binary case (1/0): mark only 1s
        elif len(lst_elements) == 2:
            data[data[marker] == lst_elements[1]].apply(
                lambda row: folium.Marker(location=[row[y], row[x]], popup=row[marker], draggable=False,
                                          icon=folium.Icon(icon="info-sign", color=lst_colors[0])).add_to(map_), axis=1)
            # normal case: mark all values
        else:
            for i in lst_elements:
                data[data[marker] == i].apply(
                    lambda row: folium.Marker(location=[row[y], row[x]], popup=row[marker], draggable=False,
                                              icon=folium.Icon(icon="info-sign", color=lst_colors[lst_elements.index(i)])).add_to(map_),
                    axis=1)

    # full screen
    plugins.Fullscreen(position="topright", title="Expand", title_cancel="Exit", force_separate_button=True).add_to(
        map_)
    return map_



@streamlit.cache_resource
def shortest_length_map(dtf, strt, ends):
    start = dtf[dtf["id"] == strt][["y", "x"]].values[0]
    end = dtf[dtf["id"] == ends][["y", "x"]].values[0]

    G = ox.graph_from_point(start, dist=50000, network_type="drive")
    G = ox.add_edge_speeds(G)
    G = ox.add_edge_travel_times(G)

    start_node = ox.distance.nearest_nodes(G, start[1], start[0])
    end_node = ox.distance.nearest_nodes(G, end[1], end[0])

    path_length = nx.shortest_path(G, source=start_node, target=end_node, method='dijkstra', weight='length')
    path_time = nx.shortest_path(G, source=start_node, target=end_node, method='dijkstra', weight='travel_time')

    map_ = plot_map(dtf, y="y", x="x", start=start, zoom=12,
                    tiles="cartodbpositron", popup="id", lst_colors=["black", "red"])

    ox.plot_route_folium(G, route=path_length, route_map=map_, color="red", weight=1)
    ox.plot_route_folium(G, route=path_time, route_map=map_, color="blue", weight=1)
    return map_, 'Shortest Path by Distance (Red):' + str(round(
        sum(ox.utils_graph.get_route_edge_attributes(G, path_length, 'length')) / 1000, 2)) + 'km | ' + \
                 str(round(sum(ox.utils_graph.get_route_edge_attributes(G, path_length, 'travel_time')) / 60,
                           2)) + 'min', 'Shortest Path by Time (Blue):' + str(round(
        sum(ox.utils_graph.get_route_edge_attributes(G, path_time, 'length')) / 1000, 2)) + 'km | ' + \
                 str(round(sum(ox.utils_graph.get_route_edge_attributes(G, path_time, 'travel_time')) / 60, 2)) + 'min'






