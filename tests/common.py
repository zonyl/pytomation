class DelegateTester(object):
    _args = []
    _kwargs = {}

    def delegate(self, *args, **kwargs):
        self._args = args
        self._kwargs = kwargs

    def get_delegate_params(self):
        return (self._args, self._kwargs)
