# Plugin to Detect Potential OLS Penetration by Traffic
# M. Faza Abel J. M. | 13620015 | 14408881

from bluesky import core, traf, stack, sim, tools
from bluesky.tools import datalog, areafilter
from bluesky.tools.geo import *

import random
import numpy as np
import time
import datetime

def unix_to_datetime(unix_timestamp):
    return datetime.datetime.fromtimestamp(int(unix_timestamp))

def init_plugin():

    # Additional initialisation code 
    OBound = OLSBoundary()

    # Configuration parameters
    config = {
        # The name of your plugin
        'plugin_name':     'OLSBoundary',

        # The type of this plugin.
        'plugin_type':     'sim'
        }
    # init_plugin() should always return the config dict.
    return config

class OLSBoundary(core.Entity):
    def __init__(self):
        self.radius = 9998.948
        self.latc = -6.1264
        self.lonc = 106.6547
        self.density = 1000
        self.mdens = 0
        self.lat_cc, self.lon_cc = 0, 0
        self.standardtime = time.time()
        headerr = "density,latitude,longitude,id,time"
        self.loggedstuff = datalog.crelog("CircleSpawnLog", None, headerr)
        super().__init__()
    
    @core.timed_function(name='OLSBoundary', dt=1)
    def OLSBoundary(self):
        # Define the inner OLS boundary circle around WIII airport
        stack.stack(f"CIRCLE inner layer {self.latc} {self.lonc} {self.radius/nm}")
        # Define the outer OLS boundary circle around WIII airport
        stack.stack(f"CIRCLE inner layer {self.latc} {self.lonc} {0.5*self.radius/nm}")
        stack.stack(f"PAN {self.latc} {self.lonc}")
        stack.stack(f"ZOOM {np.sqrt(self.radius/100)}")
        stack.stack("op")
        return