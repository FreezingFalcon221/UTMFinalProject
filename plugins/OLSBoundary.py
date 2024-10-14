# Plugin to Detect Potential OLS Penetration by Traffic
from bluesky import core, stack, traf, settings, navdb, sim, scr, tools

# Get number of aircraft
num_ac = traf.ntraf

# Get the index of the aircraft with identifier KL204 and print its latitude
idx = traf.id2idx("GIA123")
print(traf.lat[idx])