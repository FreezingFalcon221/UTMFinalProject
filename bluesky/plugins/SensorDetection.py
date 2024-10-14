# Plugin to simulate sensor (i.e. radar) detection upon entering a certain circular area
# From XXXX to DROXXXX
# Written by FreezingFalcon

from bluesky import core, traf, stack, sim, tools
from bluesky.tools import datalog, areafilter
from bluesky.tools.geo import *
from shapely import *

import numpy as np
import time
import datetime

def unix_to_datetime(unix_timestamp):
    return datetime.datetime.fromtimestamp(int(unix_timestamp))

def init_plugin():

    SDet = SensorDetection()

    # Configuration parameters
    config = {
        # The name of your plugin
        'plugin_name':     'SensorDetection',

        # The type of this plugin.
        'plugin_type':     'sim'
        }
    # init_plugin() should always return the config dict.
    return config

class SensorDetection(core.Entity):
    def __init__(self):
        self.radius = 10000
        self.latc = -6.1264
        self.lonc = 106.6547
        self.latE25L = -6.127992
        self.lonE25L = 106.685071
        self.latE25R = -6.099304
        self.lonE25R = 106.677291
        self.latE07L = -6.116856
        self.lonE07L = 106.634743
        self.latE07R = -6.148298
        self.lonE07R = 106.633058
        self.density = 1000
        self.mdens = 0
        self.lat_cc, self.lon_cc = 0, 0
        self.standardtime = time.time()
        headerr = "density,latitude,longitude,id,time"
        self.loggedstuff = datalog.crelog("CircleSpawnLog", None, headerr)
        
        # Create points within the airport to position the effectors (within airport perimeters)
        self.E25L_center = Point(self.latE25L, self.lonE25L)
        self.E25L_buffer = self.E25L_center.buffer(4.8/111.111)
        
        self.E25R_center = Point(self.latE25R, self.lonE25R)
        self.E25R_buffer = self.E25R_center.buffer(4.8/111.111)

        self.E07L_center = Point(self.latE07L, self.lonE07L)
        self.E07L_buffer = self.E07L_center.buffer(4.8/111.111)

        self.E07R_center = Point(self.latE07R, self.lonE07R)
        self.E07R_buffer = self.E07R_center.buffer(4.8/111.111)

        # Define Max Detection Range boundary circle around WIII airport
        stack.stack(f"CIRCLE DETECT25L {self.latE25L} {self.lonE25L} {0.48*self.radius/nm}")
        stack.stack(f"CIRCLE DETECT25R {self.latE25R} {self.lonE25R} {0.48*self.radius/nm}")
        stack.stack(f"CIRCLE DETECT07L {self.latE07L} {self.lonE07L} {0.48*self.radius/nm}")
        stack.stack(f"CIRCLE DETECT07R {self.latE07R} {self.lonE07R} {0.48*self.radius/nm}")

        # Define the colours of the Zones
        stack.stack(f"COLOR DETECT25L BLACK")
        stack.stack(f"COLOR DETECT25R BLACK")
        stack.stack(f"COLOR DETECT07L BLACK")
        stack.stack(f"COLOR DETECT07R BLACK")

        # Final config for ease of use
        stack.stack(f"PAN WIII")
        stack.stack(f"VIS MAP TILEDMAP")
        stack.stack(f"ZOOM 3")
        stack.stack(f"ASAS ON")
        stack.stack("op")

        super().__init__()

    @core.timed_function(name='InRangeChange_25L',dt=0.05)
    def InRangeChange_25L(self):
        inside_sensor_25L = []

        x = traf.lat
        y = traf.lon

        for i in range(len(x)):
            x_local = x[i]
            y_local = y[i]

            coord = Point(x_local, y_local)

            cond = coord.within(self.E25L_buffer)

            inside_sensor_25L.append(cond)

            if(cond):
                traf.id[i] = traf.id[i].replace("XXX","DRO")

    @core.timed_function(name='InRangeChange_25R',dt=0.05)
    def InRangeChange_25R(self):
        inside_sensor_25R = []

        x = traf.lat
        y = traf.lon

        for i in range(len(x)):
            x_local = x[i]
            y_local = y[i]

            coord = Point(x_local, y_local)

            cond = coord.within(self.E25R_buffer)

            inside_sensor_25R.append(cond)

            if(cond):
                traf.id[i] = traf.id[i].replace("XXX","DRO")

    @core.timed_function(name='InRangeChange_07L',dt=0.05)
    def InRangeChange_07L(self):
        inside_sensor_07L = []

        x = traf.lat
        y = traf.lon

        for i in range(len(x)):
            x_local = x[i]
            y_local = y[i]

            coord = Point(x_local, y_local)

            cond = coord.within(self.E07L_buffer)

            inside_sensor_07L.append(cond)

            if(cond):
                traf.id[i] = traf.id[i].replace("XXX","DRO")

    @core.timed_function(name='InRangeChange_07R',dt=0.05)
    def InRangeChange_07R(self):
        inside_sensor_07R = []

        x = traf.lat
        y = traf.lon

        for i in range(len(x)):
            x_local = x[i]
            y_local = y[i]

            coord = Point(x_local, y_local)

            cond = coord.within(self.E07R_buffer)

            inside_sensor_07R.append(cond)

            if(cond):
                traf.id[i] = traf.id[i].replace("XXX","DRO")