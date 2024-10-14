from bluesky import stack, core, traf
import numpy as np

### Initialization function of your plugin. Do not change the name of this
### function, as it is the way BlueSky recognises this file as a plugin.
def init_plugin():

    # Configuration parameters
    config = {
        # The name of your plugin
        'plugin_name':     'nb_pax',

        # The type of this plugin.
        'plugin_type':     'sim'
        }
    
    # init_plugin() should always return the config dict.
    example = Example()
    return config

class Example(core.Entity):
    ''' Example new entity object for BlueSky. '''
    def __init__(self):
        super().__init__()

        with self.settrafarrays():
            self.npassengers = np.array([])

    def create(self, n=1):
        ''' This function gets called automatically when new aircraft are created. '''
        # Don't forget to call the base class create when you reimplement this function!
        super().create(n)
        # After base creation we can change the values in our own states for the new aircraft
        self.npassengers[-n:] = [np.random.randint(0, 150) for _ in range(n)]

    @core.timed_function(name='CRE_RAND', dt=20)
    def update(self):
        ''' Periodic update function for our example entity. '''
        stack.stack('ECHO Example update: creating a random aircraft')
        stack.stack('MCRE 1')

    @stack.command(name='CHECK_PAX')
    def passengers(self, acid: 'acid', count: int = -1):
        ''' Set the number of passengers on aircraft 'acid' to 'count'. '''
        if count < 0:
            return True, f'Aircraft {traf.id[acid]} currently has {self.npassengers[acid]} passengers on board.'

        self.npassengers[acid] = count
        return True, f'The number of passengers on board {traf.id[acid]} is set to {count}.'