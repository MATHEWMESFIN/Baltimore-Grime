import streamlit as st
import pandas as pd
import geopandas as gpd
import numpy as np
from sklearn.preprocessing import LabelEncoder
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.ensemble import ExtraTreesRegressor
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import BaggingRegressor
import folium
from folium import plugins

st.set_page_config(page_title="Baltimore Grime", layout="wide")

# Load data
grimeData = pd.read_csv('Cleaned_311_Customer_Service_Request.csv')

with st.sidebar:
    st.title("Baltimore Grime Data")
    st.caption("Adjust the filters for the grime data")

    selectedCategory = st.multiselect(
        "Select a category",
        list(grimeData['Category'].unique()),
        placeholder="All"
    ) 

    sortedNeighborhoods = sorted(grimeData['Neighborhood'].unique())
    selectedNeighborhood = st.multiselect(
        "Select a neighborhood",
        sortedNeighborhoods,
        placeholder="All"
    )

filteredData = grimeData["Category"].str.contains("|".join(selectedCategory)) & \
    grimeData["Neighborhood"].str.contains("|".join(selectedNeighborhood))

def displayNeighborhoodMap(data):

    # group the data by neighborhood
    neighborhoodData = data.groupby('Neighborhood').size().reset_index(name='GrimeCount')

    # read the shapefile of the neighborhoods
    neighborhoods = gpd.read_file('Neighborhood.geojson')

    # convert the neighborhood names to uppercase
    neighborhoods['Name'] = neighborhoods['Name'].str.upper()

    # merge the neighborhood data with the shapefile by 
    neighborhoodData = neighborhoods.merge(neighborhoodData, left_on='Name', right_on='Neighborhood', how='left')

    # create a map of the neighborhoods
    neighborhoodMap = folium.Map(location=[neighborhoodData['geometry'].centroid.y.mean(), neighborhoodData['geometry'].centroid.x.mean()], zoom_start=12)

    # convert GrimeCount to float64
    neighborhoodData['GrimeCount'] = neighborhoodData['GrimeCount'].astype('float64')

    # add the neighborhood data to the map
    cp = folium.Choropleth(
        geo_data=neighborhoodData,
        name='choropleth',
        data=neighborhoodData,
        columns=['Name', 'GrimeCount'],
        key_on='feature.properties.Name',
        fill_color='YlOrRd',
        fill_opacity=0.7,
        line_opacity=0.2,
        legend_name='Number of Grime Reports',
        highlight=True
    ).add_to(neighborhoodMap)

    neigborhoodDataIndexed = neighborhoodData.set_index('Name')

    # add the neighborhood names to the map
    for n in cp.geojson.data['features']:
        n['properties']['GrimeCount'] = neigborhoodDataIndexed.loc[n['properties']['Name']]['GrimeCount']

    folium.GeoJsonTooltip(fields=['Name', 'GrimeCount']).add_to(cp.geojson)

    neighborhoodMap.save('neighborhoodMap.html')
    st.components.v1.html(open('neighborhoodMap.html', 'r').read(), height=600)

st.metric(label="Total Grime Reports", value=grimeData[filteredData].shape[0])

st.header("Neighborhood Map")
st.write("The map below shows the number of grime reports in each neighborhood.")
displayNeighborhoodMap(grimeData[filteredData])