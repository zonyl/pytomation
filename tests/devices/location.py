from .ha_device import HADevice

class Location(HADevice):
    STATES = ['SUNSET', 'TWILIGHT', 'SUNRISE']
    
    def lat_and_long(self, lat, long):
        pass
        