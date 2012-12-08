from pytomation.devices import InterfaceDevice

class GenericInput(InterfaceDevice):
    def _init(self, *args, **kwargs):
        self._read_only = True
