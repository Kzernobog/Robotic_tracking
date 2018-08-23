
class Packet(object):

    def __init__(self): 
        self._data = []

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, value):
        #TODO: check for appropriate value
        self._data = value
