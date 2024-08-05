import geopandas as gpd
from shapely import wkt
from shapely.geometry import Point,MultiPolygon
import requests
import pandas as pd
import time

# Function to convert WKT strings to Point objects
def convert_to_geometry(geom):
    """
    Converts WKT (Well-Known Text) strings to appropriate Shapely geometry objects.
    If the input is already a valid Shapely geometry object, it returns it directly.
    For unsupported types, it logs an error and returns None.
    """
    if isinstance(geom, str):
        try:
            return wkt.loads(geom)
        except Exception as e:
            print(f"Error converting {geom}: {e}")
            return None
    elif isinstance(geom, (Point, MultiPolygon)):
        return geom
    else:
        print(f"Unsupported type: {type(geom)}")
        return None

def spatial_join(df1, df2, col1, col2):
    """
    This function creates a spatial join between df1 and df2 using the specified geometry columns col1 and col2.
    """
    # Ensure geometries are valid
    df1[col1] = df1[col1].apply(convert_to_geometry)
    df2[col2] = df2[col2].apply(convert_to_geometry)

    # Converting to geo dataframes
    df1_gdf = gpd.GeoDataFrame(df1, geometry=col1)
    df2_gdf = gpd.GeoDataFrame(df2, geometry=col2)

    # Apply a smaller buffer to the polygons (e.g., 0.0001 degree)
    df2_gdf[col2] = df2_gdf.buffer(0.001)

    # Set the CRS
    df1_gdf.crs = 'EPSG:32612'
    df2_gdf.crs = 'EPSG:32612'

    # Ensure both GeoDataFrames are in the same CRS
    df1_gdf = df1_gdf.to_crs(df2_gdf.crs)

    # Perform the spatial join
    df1_df2_gdf = gpd.sjoin(df1_gdf, df2_gdf, how='left', predicate='within')

    #dropping any rows with data imputation columns
    df1_df2_gdf = df1_df2_gdf.dropna(subset=['Neighbourhood Name','Civic Ward'])

    #Drop duplicates based on 'Reference Number', keeping the first occurrence
    df1_df2_gdf = df1_df2_gdf.drop_duplicates(subset='Reference Number', keep='first')

    # Reset index for alignment
    df1_df2_gdf = df1_df2_gdf.reset_index(drop=True)
    df1 = df1.reset_index(drop=True)    

    return df1,df1_df2_gdf

def spatial_join_imputation(df1, df2, col1, col2, col3, col4,key_col):
    """
    Fills missing 'Neighbourhood' and 'Ward' values in the original DataFrame df1 using values from df2.
    """

    merged_data = df1.merge(df2[[key_col, col2, col4]], 
                         on=key_col, 
                         how='left')


    # Fill missing values in df1 columns with values from df2
    merged_data[col1] = merged_data[col1].fillna(merged_data[col2])
    merged_data.loc[(merged_data[col3].isna()) | (merged_data[col3].astype(str).str.isnumeric()),col3] = merged_data[col4]
    

    # Drop unnecessary columns and remove duplicates if needed
    merged_data = merged_data.drop(columns=['Neighbourhood Name', 'Civic Ward'])
    merged_data = merged_data.dropna(subset='Reference Number')

    return merged_data

def batch_impute_address(df,col,lat,long,batch_size=100):
    """
    Impute missing address in batches 
    """
    for start in range(0,len(df),batch_size):
        end = min(start+batch_size,len(df))
        batch = df.iloc[start:end]

        for index, row in batch.iterrows():
            if pd.isna(row[col]) and not (pd.isna(row[lat]) or pd.isna(row[long])):
                value = get_address_from_lat_long(row[lat],row[long])
                print(value)
                df.at[index,col] = value

        #Delay to respect API rate limits
        time.sleep(1)  # Adjust delay based on rate limits

        return df
    
def get_address_from_lat_long(lat, long):
    """
    This function returns the road address for given latitude and longitude using the OpenStreetMap Nominatim API.
    """
    url = f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={long}&format=json"
    headers = {
        'User-Agent': '311-data/2.0 (harmanpreet.kaur01@outlook.com)'
    }
    response = requests.get(url, headers=headers)
    
    # Check if the request was successful
    if response.status_code == 200:
        try:
            results = response.json()
            if 'address' in results:
                return results['address'].get('road', 'Unknown')
            return 'Unknown'
        except requests.exceptions.JSONDecodeError:
            return 'Invalid JSON response'
    else:
        return f"Error: {response.status_code}"
    

# def address_impute(df, col, lat, long):
#     """
#     This function performs address imputation for null values in the specified column using the get_address_from_lat_long
#     function, utilizing the 'Lat' and 'Long' values through the OpenStreetMap API.
#     """
#     for index, row in df[df[col].isna()].iterrows():
#         try:
#             address = get_address_from_lat_long(row[lat], row[long])
#             if address:
#                 df.at[index, col] = address
#             else:
#                 print(f"Address not found for index {index} (lat: {row[lat]}, long: {row[long]})")
#         except Exception as e:
#             print(f"Error at index {index}: {e}")
#     return df

def change_to_int(df, *cols):
        """
        Changing data type to int
        """
        for col in cols:
            df[col] = df[col].astype(int)

        return df

def change_to_float(df, *cols):
        """
        Changing data type to float
        """
        for col in cols:
            df[col] = df[col].astype(float)
        
        return df

def change_to_object(df, *cols):
        """
        Changing data type to object
        """
        for col in cols:
            df[col] = df[col].astype(str)

        return df

def change_to_datetime(df, *cols):
        """
        Changing data type to datetime
        """
        for col in cols:
            df[col] = pd.to_datetime(df[col])

        return df

def change_to_timedelta(df, *cols):
        for col in cols:
            df[col] = pd.to_timedelta(df[col], errors='coerce')

        return df

def change_to_numeric_int(df, *cols):
        for col in cols:
            df[col] = pd.to_numeric(df[col], errors='coerce')
            df = df.dropna(subset=[col])
            df[col] = df[col].astype('int64').abs()

        return df

def clean_and_convert(df):
    """
    This function performs type conversion and cleanup on the provided DataFrame.
    It converts columns to the appropriate types, handles errors and returns the cleaned dataset
    """  
    df = change_to_int(df, 'Count', 'Calendar Year')
    df = change_to_float(df, 'Lat', 'Long')
    df = change_to_object(df, 'Request Status', 'Service Category', 'Service Code', 
                        'Business Unit', 'Neighbourhood', 'Community League', 
                        'Ward', 'Address', 'Location', 'Ticket Source')
    df = change_to_datetime(df, 'Date Created', 'Date Closed')
    df = change_to_numeric_int(df, 'Reference Number')

    return df





