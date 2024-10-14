# Plugin to echo aircraft data
# Written by FreezingFalcon
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

    techo = TrafEcho()
    tmod = TrafModify()
    # scomp = StatComp()
    # talt = TrafAlt()
    # tdel = TrafDelete()

    # Configuration parameters
    config = {
        # The name of your plugin
        'plugin_name':     'TrafEcho',

        # The type of this plugin.
        'plugin_type':     'sim'
        }
    # init_plugin() should always return the config dict.
    return config

# Sebaiknya jangan 2 classes in a plugin(?)
class TrafEcho(core.Entity):
    ''' Example new entity object for BlueSky. '''
    def __init__(self):
        super().__init__()
    @core.timed_function(name="TrafEcho", dt=5)
    def update(self):
        stack.stack('ECHO nb aircraft: {}'.format(np.size(traf.id)))
        stack.stack('ECHO lat aircraft: {}'.format(np.array(traf.lat)))
        stack.stack('ECHO long aircraft: {}'.format(np.array(traf.lon)))
        stack.stack('ECHO alt aircraft: {}'.format(np.array(traf.alt)))

# Ceritanya kalau ganti V/S tapi targeting semua traffic
class TrafModify(core.Entity):
    def __init__(self):
        super().__init__()
    @core.timed_function(name='TrafModify', dt=5)
    def update(self):
        cond1 = (traf.alt >= 762)
        cond2 = (traf.alt < 782)
        cond = cond1 & cond2
        traf.alt[cond] = 0

