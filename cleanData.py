import pandas as pd
import geopandas as gpd

 # Function to clean the neighborhood column
def clean_neighborhood_column(data):
    # empty the Neighborhood column
    cleaned_data = data.drop(columns=['Neighborhood'])

    # create a new column 'Neighborhood' using the neighborhood shapefile
    # load the neighborhood shapefile
    neighborhoods = gpd.read_file("Neighborhood.geojson")
    # create a new column 'Neighborhood' by mapping the 'Latitude' and 'Longitude' columns to the neighborhood shapefile
    cleaned_data['Neighborhood'] = gpd.points_from_xy(data['Longitude'], data['Latitude']).map(
        lambda x: neighborhoods[neighborhoods.contains(x)]['Name'].values[0] if len(neighborhoods[neighborhoods.contains(x)]) > 0 else 'UNKNOWN')
    
    # drop the 'UNKNOWN' rows
    cleaned_data = cleaned_data[cleaned_data['Neighborhood'] != 'UNKNOWN']

    # make the neighborhood values uppercase
    cleaned_data['Neighborhood'] = cleaned_data['Neighborhood'].str.upper()

    return cleaned_data

grimedata = pd.read_csv('Cleaned_311_Customer_Service_Request.csv')
cleaned_grimedata = clean_neighborhood_column(grimedata)
cleaned_grimedata.to_csv('Cleaned_311_Customer_Service_Request.csv', index=False)