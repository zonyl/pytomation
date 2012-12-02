
class PytomationObject(object):
    instances = []
    def __init__(self, *args, **kwargs):
        self._po_common(*args, **kwargs)

    def _po_common(self, *args, **kwargs):
        self.instances.append(self)
