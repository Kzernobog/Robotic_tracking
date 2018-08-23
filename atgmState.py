# class that maintains information of the current state of the ATGM Turret
class ATGMState(object):
    # constructor
    def __init__(self):
        self._azimuth_steps = 0
        self._elevation_steps = 0

    # hard reset
    def reset(self):
        self._azimuth_steps = 0
        self._elevation_steps = 0

    @property
    def Azimuth_steps(self):
        return self._azimuth_steps

    @Azimuth_steps.setter
    def Azimuth_steps(self, value):
        self._azimuth_steps = value

    @property
    def Elevation_steps(self):
        return self._elevation_steps

    @Elevation_steps.setter
    def Elevation_steps(self, value):
        self._elevation_steps = value
