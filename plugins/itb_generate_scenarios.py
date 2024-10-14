import datetime
import os, sys
import numpy as np

id_list = ['GA001', 'GA002', 'GA003', 'GA004', 'GA005']
nb_ac = len(id_list)

ac_type = "B737"

## command to make aircraft
## CRE acid, type, lat, lon, hdg, alt, spd

## latlon
min_lat = -6.276027
max_lat = -5.925761
min_lon = 106.457062
max_lon = 106.967421

lat_list = np.random.uniform(min_lat, max_lat, nb_ac)
lon_list = np.random.uniform(min_lon, max_lon, nb_ac)

## hdg
min_hdg = 0
max_hdg = 359

hdg_list = np.random.uniform(min_hdg, max_hdg, nb_ac)

## alt

min_alt = 34 ## in 1000 ft
max_alt = 36 ## in 1000 ft

alt_list = np.random.randint(min_alt, max_alt, nb_ac)

## spd
min_spd = 160
max_spd = 170

spd_list = np.random.randint(min_spd, max_spd, nb_ac)

## write into .scn file
f = open("scenario/randomized.scn", "w")

## CRE acid, type, lat, lon, hdg, alt, spd
f.write(f"00:00:00.00> PAN WIII\n")
f.write(f"00:00:00.00> TRAIL ON\n")

for i in range(nb_ac):
    f.write(f"00:00:00.00> CRE {id_list[i]} {ac_type} {lat_list[i]} {lon_list[i]} {hdg_list[i]} {alt_list[i]} {spd_list[i]}\n")

f.close()
