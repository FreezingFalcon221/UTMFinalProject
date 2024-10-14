import bluesky as bs
from bluesky.core import Entity, timed_function
from bluesky.stack import command
from bluesky import stack, core
from bluesky.tools import datalog
from bluesky.tools.aero import ft

import pandas as pd
from shapely import Point, Polygon

def init_plugin():
    # Configuration parameters
    config = {
        'plugin_name': 'reroute',
        'plugin_type': 'sim',
        'reset': reset
    }
    
    bs.traf.reroute = Reroute()
    return config

def reset():
    bs.traf.reroute.reset()

class Reroute(Entity):
    def __init__(self):
        super().__init__()
        self.restrictdict = {}
        
    def check_coordinates_is_closed(self, coordinates):
        return coordinates[0] == coordinates[-1]

    @stack.command(name="RESTRICTAREA")
    def create_restrictarea(self, name, filename):
        df = pd.read_csv(f"scenario/{filename}")
        lat = df['lat']
        lon = df['lon']

        coordinates = []

        for i in range(len(df)):
            coordinates.append((lat[i], lon[i]))

        self.restrictdict[name] = coordinates

        if(not self.check_coordinates_is_closed(coordinates)):
            coordinates.append(coordinates[0])

        coordinates_string = ""

        for coordinate in coordinates:
            coordinates_string += str(coordinate[0]) + ", " + str(coordinate[1]) + " "

        stack.stack(f"POLY {name} {coordinates_string}")
        stack.stack(f"ECHO CREATED RESTRICTAREA {name}")

        self.restrictdict[name] = Polygon(coordinates)
        
    @core.timed_function(name="check_waypoints", dt=1.0)
    def check_waypoints(self):        
        for i in range(bs.traf.ntraf):
            for j in range(0,bs.traf.ap.route[i].nwp):
                id = bs.traf.id[i]

                txt = bs.traf.ap.route[i].wpname[j]
                print(txt)

                ## manipulate the waypoint here
                wppoint = Point(bs.traf.ap.route[i].wplat[j], bs.traf.ap.route[i].wplon[j])

                for key in self.restrictdict.keys():
                    if(self.restrictdict[key].contains(wppoint)):
                        ## this part can be replaced using path finding algorithm
                        ## such as Dijsktra or A*
                        stack.stack(f"{id} AFTER {txt} ADDWPT RUPKA")
                        stack.stack(f"DELWPT {id} {txt}")
                    
    