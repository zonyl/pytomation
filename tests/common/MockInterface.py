from pytomation.interfaces import HAInterface

class MockInterface(object):
    _written = None
    _responses = {}
    _response_q = None

    def __init__(self, *args, **kwargs):
        pass

    def write(self, data=None):
        self._written = data
        self._response_q = self._get_response(data)

    def read(self, count=None):
        response = ""
        if self._response_q:
            if not count:
                count = len(self._response_q)
            response = self._response_q[:count]

            if count >= len(self._response_q):
                self._response_q = None
            else:
                self._response_q = self._response_q[count:]
        return response

    def _get_response(self, written):
        try:
            return self._responses[self._written]
        except:
            return None

    def add_response(self, response_set):
        self._responses.update(response_set)
        return True
