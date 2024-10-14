# Plugin to terminate a flight when entering a restricted airspace (Zone A) at Jakarta's WIII airport
# Written by FreezingFalcon

from bluesky import core, traf, stack, sim, tools
from bluesky.tools import datalog, areafilter
from bluesky.tools.geo import *
from shapely import *

import time
import datetime

def unix_to_datetime(unix_timestamp):
    return datetime.datetime.fromtimestamp(int(unix_timestamp))

def init_plugin():

    AOLS = AirportOLS()

    # Configuration parameters
    config = {
        # The name of your plugin
        'plugin_name':     'AirportOLS',

        # The type of this plugin.
        'plugin_type':     'sim'
        }
    # init_plugin() should always return the config dict.
    return config

class AirportOLS(core.Entity):
    def __init__(self):
        self.radius = 10000
        self.latc = -6.1264
        self.lonc = 106.6547
        self.lat25L = -6.129701
        self.lon25L =  106.674772
        self.lat25R = -6.108223
        self.lon25R = 106.669058
        self.lat07L = -6.121538
        self.lon07L = 106.637583
        self.lat07R = -6.142669
        self.lon07R = 106.643556
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
        
        # Create a point and circle buffers to check the drone intrusion
        self.circle_center = Point(self.latc, self.lonc)
        self.circle_buffer = self.circle_center.buffer(4/111.111)

        self.R25L_center = Point(self.lat25L, self.lon25L)
        self.R25L_buffer = self.R25L_center.buffer(4/111.111)

        self.R25R_center = Point(self.lat25R, self.lon25R)
        self.R25R_buffer = self.R25R_center.buffer(4/111.111)

        self.R07L_center = Point(self.lat07L, self.lon07L)
        self.R07L_buffer = self.R07L_center.buffer(4/111.111)

        self.R07R_center = Point(self.lat07R, self.lon07R)
        self.R07R_buffer = self.R07R_center.buffer(4/111.111)
        
        # Create points within the airport to position the effectors (within airport perimeters)
        self.E25L_center = Point(self.latE25L, self.lonE25L)
        self.E25L_buffer = self.E25L_center.buffer(4/111.111)
        
        self.E25R_center = Point(self.latE25R, self.lonE25R)
        self.E25R_buffer = self.E25R_center.buffer(4/111.111)

        self.E07L_center = Point(self.latE07L, self.lonE07L)
        self.E07L_buffer = self.E07L_center.buffer(4/111.111)

        self.E07R_center = Point(self.latE07R, self.lonE07R)
        self.E07R_buffer = self.E07R_center.buffer(4/111.111)

        # Define Zone B boundary circle around WIII airport
        stack.stack(f"CIRCLE ZONEB {self.latc} {self.lonc} {self.radius/nm}")
        # Define Zone A boundary circle around WIII airport
        stack.stack(f"CIRCLE ZONEA25L {self.lat25L} {self.lon25L} {0.4*self.radius/nm}")
        stack.stack(f"CIRCLE ZONEA25R {self.lat25R} {self.lon25R} {0.4*self.radius/nm}")
        stack.stack(f"CIRCLE ZONEA07L {self.lat07L} {self.lon07L} {0.4*self.radius/nm}")
        stack.stack(f"CIRCLE ZONEA07R {self.lat07R} {self.lon07R} {0.4*self.radius/nm}")
        # Define Zone C boundary circle around WIII airport
        stack.stack(f"CIRCLE ZONEC {self.latc} {self.lonc} {1.5*self.radius/nm}")
        # Define Zone D boundary circle around WIII airport
        stack.stack(f"CIRCLE ZONED {self.latc} {self.lonc} {5*self.radius/nm}")
        # Define the square effector exclusion zone around WIII airport
        stack.stack(f"POLYALT SQUARE 0 122 -6.141335 106.607423 -6.08574 106.640835 -6.110221 106.705147 -6.165499 106.671481")
        self.polycoords = ((-6.141335, 106.607423), (-6.08574, 106.640835), (-6.110221, 106.705147), (-6.165499, 106.671481))
        self.polygon = Polygon(self.polycoords)
        self.poly_center = centroid(self.polygon)
        self.poly_buffer = self.poly_center.buffer(4/111.111)
        # Define the colours of the Zones
        stack.stack(f"COLOR ZONEB ORANGE")
        stack.stack(f"COLOR ZONEA25L RED")
        stack.stack(f"COLOR ZONEA25R RED")
        stack.stack(f"COLOR ZONEA07L RED")
        stack.stack(f"COLOR ZONEA07R RED")
        stack.stack(f"COLOR ZONEC YELLOW")
        stack.stack(f"COLOR ZONED GREEN")
        stack.stack(f"COLOR SQUARE ORANGE")

        # Final config for ease of use
        stack.stack(f"PAN WIII")
        stack.stack(f"VIS MAP TILEDMAP")
        stack.stack(f"ZOOM 3")
        stack.stack(f"ASAS ON")
        stack.stack("op")

        self.gun_counter = 0
        self.gun_duration = 5
        self.refresh_duration = 0.05
        self.max_gun_counter = self.gun_duration/self.refresh_duration

        self.jammer_counter = 0
        self.jammer_duration = 20
        self.max_jammer_counter = self.jammer_duration/self.refresh_duration

        self.laser_counter = 0
        self.laser_duration = 10
        self.max_laser_counter = self.laser_duration/self.refresh_duration

        super().__init__()

    # Checking if target is in Zone A for Runway 25L
    @core.timed_function(name='check_circle_25L',dt=0.05)
    def check_circle_25L(self):
        inside_25L = []
        inside_poly_25L = []

        x = traf.lat
        y = traf.lon

        for i in range(len(x)):
            x_local = x[i]
            y_local = y[i]

            coord = Point(x_local,y_local)

            cond_circle = coord.within(self.E25L_buffer)

            cond_polygon = coord.within(self.polygon)

            cond = (cond_circle & ~cond_polygon)

            inside_25L.append(cond_circle)

            inside_poly_25L.append(cond_polygon)

            weapon = 'jammer'

            if(cond_circle):
                if(weapon == "jammer"):
                    stack.stack('ECHO {}/{}'.format(self.jammer_counter,self.max_jammer_counter))
                    self.jammer_counter += 1
                    if(self.jammer_counter >= self.max_jammer_counter):
                        stack.stack('ALT {}, 0, -1000'.format(traf.id[i]))
                        stack.stack('SPD {}, 0'.format(traf.id[i]))
                        stack.stack('ECHO Target forced to land.')
                        self.jammer_counter = 0
                elif(weapon == "gun"):
                    stack.stack('ECHO {}/{}'.format(self.gun_counter,self.max_gun_counter))
                    self.gun_counter += 1
                    if(self.gun_counter >= self.max_gun_counter):
                        stack.stack('ECHO Target shot down.')
                        stack.stack('DEL {}'.format(traf.id[i]))
                        self.gun_counter = 0
                elif(weapon == "laser"):
                    stack.stack('ECHO {}/{}'.format(self.laser_counter,self.max_laser_counter))
                    self.laser_counter += 1
                    if(self.laser_counter >= self.max_laser_counter):
                        stack.stack('ECHO Target shot down.')
                        stack.stack('DEL {}'.format(traf.id[i]))
                        self.laser_counter = 0

    # Checking if target is in Zone A for Runway 25R
    @core.timed_function(name='check_circle_25R',dt=0.05)
    def check_circle_25R(self):
        inside_25R = []
        inside_poly_25R = []

        x = traf.lat
        y = traf.lon

        for i in range(len(x)):
            x_local = x[i]
            y_local = y[i]

            coord = Point(x_local,y_local)

            cond_circle = coord.within(self.E25R_buffer)

            cond_polygon = coord.within(self.polygon)

            cond = (cond_circle & ~cond_polygon)

            inside_25R.append(cond_circle)

            inside_poly_25R.append(cond_polygon)

            weapon = 'jammer'

            if(cond_circle):
                if(weapon == "jammer"):
                    stack.stack('ECHO {}/{}'.format(self.jammer_counter,self.max_jammer_counter))
                    self.jammer_counter += 1
                    if(self.jammer_counter >= self.max_jammer_counter):
                        stack.stack('ALT {}, 0, -1000'.format(traf.id[i]))
                        stack.stack('SPD {}, 0'.format(traf.id[i]))
                        stack.stack('ECHO Target forced to land.')
                        self.jammer_counter = 0
                elif(weapon == "gun"):
                    stack.stack('ECHO {}/{}'.format(self.gun_counter,self.max_gun_counter))
                    self.gun_counter += 1
                    if(self.gun_counter >= self.max_gun_counter):
                        stack.stack('ECHO Target shot down.')
                        stack.stack('DEL {}'.format(traf.id[i]))
                        self.gun_counter = 0
                elif(weapon == "laser"):
                    stack.stack('ECHO {}/{}'.format(self.laser_counter,self.max_laser_counter))
                    self.laser_counter += 1
                    if(self.laser_counter >= self.max_laser_counter):
                        stack.stack('ECHO Target shot down.')
                        stack.stack('DEL {}'.format(traf.id[i]))
                        self.laser_counter = 0

    # Checking if target is in Zone A for Runway 07L
    @core.timed_function(name='check_circle_07L',dt=0.05)
    def check_circle_07L(self):
        inside_07L = []
        inside_poly_07L = []

        x = traf.lat
        y = traf.lon

        for i in range(len(x)):
            x_local = x[i]
            y_local = y[i]

            coord = Point(x_local,y_local)

            cond_circle = coord.within(self.E07L_buffer)

            cond_polygon = coord.within(self.polygon)

            cond = (cond_circle & ~cond_polygon)

            inside_07L.append(cond_circle)

            inside_poly_07L.append(cond_polygon)

            weapon = 'jammer'

            if(cond_circle):
                if(weapon == "jammer"):
                    stack.stack('ECHO {}/{}'.format(self.jammer_counter,self.max_jammer_counter))
                    self.jammer_counter += 1
                    if(self.jammer_counter >= self.max_jammer_counter):
                        stack.stack('ALT {}, 0, -1000'.format(traf.id[i]))
                        stack.stack('SPD {}, 0'.format(traf.id[i]))
                        stack.stack('ECHO Target forced to land.')
                        self.jammer_counter = 0
                elif(weapon == "gun"):
                    stack.stack('ECHO {}/{}'.format(self.gun_counter,self.max_gun_counter))
                    self.gun_counter += 1
                    if(self.gun_counter >= self.max_gun_counter):
                        stack.stack('ECHO Target shot down.')
                        stack.stack('DEL {}'.format(traf.id[i]))
                        self.gun_counter = 0
                elif(weapon == "laser"):
                    stack.stack('ECHO {}/{}'.format(self.laser_counter,self.max_laser_counter))
                    self.laser_counter += 1
                    if(self.laser_counter >= self.max_laser_counter):
                        stack.stack('ECHO Target shot down.')
                        stack.stack('DEL {}'.format(traf.id[i]))
                        self.laser_counter = 0

    # Checking if target is in Zone A for Runway 07R
    @core.timed_function(name='check_circle_07R',dt=0.05)
    def check_circle_07R(self):
        inside_07R = []
        inside_poly_07R = []

        x = traf.lat
        y = traf.lon

        for i in range(len(x)):
            x_local = x[i]
            y_local = y[i]

            coord = Point(x_local,y_local)

            cond_circle = coord.within(self.E07R_buffer)

            cond_polygon = coord.within(self.polygon)

            cond = (cond_circle & ~cond_polygon)

            inside_07R.append(cond_circle)

            inside_poly_07R.append(cond_polygon)

            weapon = 'jammer'

            if(cond_circle):
                if(weapon == "jammer"):
                    stack.stack('ECHO {}/{}'.format(self.jammer_counter,self.max_jammer_counter))
                    self.jammer_counter += 1
                    if(self.jammer_counter >= self.max_jammer_counter):
                        stack.stack('ALT {}, 0, -1000'.format(traf.id[i]))
                        stack.stack('SPD {}, 0'.format(traf.id[i]))
                        stack.stack('ECHO Target forced to land.')
                        self.jammer_counter = 0
                elif(weapon == "gun"):
                    stack.stack('ECHO {}/{}'.format(self.gun_counter,self.max_gun_counter))
                    self.gun_counter += 1
                    if(self.gun_counter >= self.max_gun_counter):
                        stack.stack('ECHO Target shot down.')
                        stack.stack('DEL {}'.format(traf.id[i]))
                        self.gun_counter = 0
                elif(weapon == "laser"):
                    stack.stack('ECHO {}/{}'.format(self.laser_counter,self.max_laser_counter))
                    self.laser_counter += 1
                    if(self.laser_counter >= self.max_laser_counter):
                        stack.stack('ECHO Target shot down.')
                        stack.stack('DEL {}'.format(traf.id[i]))
                        self.laser_counter = 0
