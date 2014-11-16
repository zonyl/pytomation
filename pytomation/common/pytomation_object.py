from .pyto_logging import PytoLogging

class PytomationObject(object):
    instances = {}
    name_to_id_map = {}
    sorted_names_by_length =[]
    
    def __init__(self, *args, **kwargs):
        self._type_id = None
        self._po_common(*args, **kwargs)

    def _po_common(self, *args, **kwargs):
        
        self._logger = PytoLogging(self.__class__.__name__)
        self._type_id = str(self.__class__.__name__) + str(len(self.instances))
        self.instances[self._type_id] = self
        self._name = kwargs.get('name', self._type_id)
        self.name_to_id_map[self._name.lower()] = self.type_id
        self.sorted_names_by_length.append(self._name.lower())
        self.sorted_names_by_length.sort(key=len)
        self.sorted_names_by_length.reverse()
            
        try:
            self._logger.debug('Object created: {name} {obj}'.format(
                                                                     name=self._name,
                                                                     obj=str(self))
                               )
        except Exception, ex:
            pass
        
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
    
    @property
    def type_name(self):
        return self.__class__.__name__
    
    @property
    def type_id(self):
        return self._type_id