from pytomation.interfaces import *
from pytomation.devices import *

whitepi = Kodi(host="http://10.0.1.1/jsonrpc")
blackpi = Kodi(host="http://10.0.1.2/jsonrpc")

whitepi.command((Command.MESSAGE, 'Pytomation','Starting'))
blackpi.command((Command.MESSAGE, 'Pytomation','Starting'))

web = HTTPServer()

ozw = Open_zwave(serialDevicePath='/dev/ttyUSB0')
cm19a = Mochad(TCP('127.0.0.1',1099))

ph_standard = Location('41.500000', '-81.400000',
        tz='America/New_York',
        mode=Location.MODE.STANDARD,
        is_dst=True,
        name='Standard Photocell')
        
lmoz_office = Light(
        #address="0184c44a.6.26.1.0",
        address="6",
        devices=ozw,
        name="OpenZwave Dimmer"
)

lm_office = Light(
        address='A2',
        #initial=ph_standard,
        devices=(cm19a,
                ph_standard,
                ),
        name='Office lamp',
        send_always=True,
        )


whitepi.command((Command.MESSAGE, 'Pytomation','Started'))
blackpi.command((Command.MESSAGE, 'Pytomation','Started'))
