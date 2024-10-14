import pandas as pd
import numpy as np
from math import *

from shapely import Point

def get_tangent_angle(drone_position, airport_center, radius):
    dx = airport_center.x - drone_position.x
    dy = airport_center.y - drone_position.y
    d = sqrt(dx**2 + dy**2)

    if(d > radius):
        theta = atan2(dy, dx)
        beta = asin(radius/d)

        return degrees(theta - beta + 90), degrees(theta + beta + 90)
    
def lat_lon_to_meters(lat1, lon1, lat2, lon2):
    """
    Convert latitude and longitude coordinates to meters
    in terms of x and y coordinates
    """
    # Constants for approximate conversion
    # One degree of latitude is approximately 111.32 kilometers
    # One degree of longitude varies depending on the latitude, but approximately 111.32 kilometers at the equator
    # and gradually reducing to 0 kilometers at the poles.
    # For simplicity, let's assume one degree of longitude is 111.32 kilometers.
    lat_deg_to_meters = 111320
    lon_deg_to_meters = 111320

    # Calculate the difference in latitude and longitude
    lat_diff = lat2 - lat1
    lon_diff = lon2 - lon1

    # Calculate the distances in meters along latitude and longitude
    y = lat_diff * lat_deg_to_meters
    x = lon_diff * lon_deg_to_meters

    return x, y

def generate_random_lat_lon_within_radius(center, radius):
    """
    Generate a random latitude and longitude within a circular area defined by center coordinates and radius.
    """
    # Generate random offsets within the bounding box of the circle
    theta = np.random.uniform(0, 360)
    spawn_rad = np.random.uniform(0.98*radius, 1.02*radius)

    dx = spawn_rad * cos(radians(theta))
    dy = spawn_rad * sin(radians(theta))

    print("dist: ", sqrt(dx**2 + dy**2))

    lat = center[0] + (180 / pi) * (dy / 6378137)
    lon = center[1] + (180 / pi) * (dx / 6378137) / cos(center[0] * pi / 180)

    return lat, lon

def write_line(text,file_id):
    name = f"testscen_{file_id}"
    with open(f'scenario/{name}.scn', 'a') as fd:
        fd.write(text + '\n')

def df_to_scenario(df, file_id):
    for idx, row in df.iterrows():
        text = f"{'00:00:00.00>'} CRE DRO{idx:04d} M600 {row.lat} {row.lon} {row.heading} {row.alt} {row.spd}"
        write_line(text, file_id)

def main():
    center = (-6.1264, 106.6547)  # Soekarno-Hatta International Airport

    # Radius of the circular area in meters
    radius = 15000  # 15 kilometers
    radius_circle = 10000 # 10 km

    # Number of random points to generate
    num_points = 20
    
    # Generate random latitudes and longitudes within the circular area
    random_lat_lons = [generate_random_lat_lon_within_radius(center, radius) for _ in range(num_points)]

    lat_list = []
    lon_list = []
    heading_list = []
    alt_list = np.random.uniform(50, 100, size = num_points)
    spd_list = np.random.uniform(10, 30, size = num_points)

    # Print the generated random latitudes and longitudes
    for i, lat_lon in enumerate(random_lat_lons, 1):
        drone_position_lat, drone_position_lon = lat_lon
        lat_list.append(drone_position_lat)
        lon_list.append(drone_position_lon)

        drone_position = lat_lon_to_meters(drone_position_lat, drone_position_lon, center[0], center[1])

        drone_position = Point(drone_position)
        airport_position = Point(0,0)
        beta1, beta2 = get_tangent_angle(drone_position, airport_position, radius_circle)
        heading_ = np.random.uniform(beta1, beta2)
        heading_list.append(heading_)

        # print(f"Random Point {i}: Latitude={lat_lon[0]}, Longitude={lat_lon[1]}, beta: {beta1},{beta2}")


    data_dict = {
        'lat': lat_list,
        'lon': lon_list,
        'heading': heading_list,
        'alt': alt_list,
        'spd': spd_list
    }

    df = pd.DataFrame(data_dict)

    df_to_scenario(df, 'test_scen.scn')
    df.to_csv('scenario.csv')
    

if __name__ == "__main__":
    main()