

class GenericVar:

    def __init__(self, *args):
        assert len(args) in (0, 1)
        self._has_value = False
        self._value = None
        if len(args) == 1:
            self.value = args[0]

    @property
    def has_value(self):
        return self._has_value

    @property
    def value(self):
        if not self._has_value:
            raise NameError('generic variable was not yet set to any concrete value')
        return self._value

    @value.setter
    def value(self, val):
        self._has_value = True
        self._value = val

    def unset(self):
        self._has_value = False
        self._value = None
