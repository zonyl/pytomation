from .logging import Logging

class PytomationObject(object):
    instances = []
    def __init__(self, *args, **kwargs):
        self._po_common(*args, **kwargs)

    def _po_common(self, *args, **kwargs):
        
        self._logger = Logging(self.__class__.__name__)
        self._name = kwargs.get('name', None)
        self._logger.debug('Object created: {name} {obj}'.format(
                                                                 name=self._name,
                                                                 obj=str(self))
                           )
        self.instances.append(self)
        
    @property
    def name(self):
        return self._name
    
    @name.setter
    def name(self, value):
        self._name = value
        return self._name
    
    @property
    def name_ex(self):
        return self._name
    
    @name_ex.setter
    def name_ex(self, value):
        self._name = value
        return self._name