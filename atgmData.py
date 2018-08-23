# TODO: possible optimisations
#       decrease number of times _update_state() is called
class ATGMData(object):
    """
    Class description
    This class encapsulates the data that has to be sent to the driver
    controlling Azimuth and Elevation motors of the robotic ATGM.
    The individual properties can be accessed through the pythonic property
    interface.
    The final command for a given state is exposed through the <command>
    function.
    Make sure that all the individual variables are fed data(in integer
    format).
    The various property fields are as follows
    Azimuth Direction - int 0 for Anti, int 1 for clockwise
    Azimuth Resolution - int values between 0-15
    Azimuth RPM - int values between 0-255
    Azimuth steps - a 4 byte integer value

    Likewise for Elevation
    """
    # constructor 
    def __init__(self):
        # string representing the current state of data
        self._command_string = [] 

        self.DIRCONST = self._value_to_bytes(0, 1)
        self.STEPSCONST = self._value_to_bytes(80000, 4)
        self.RESCONST = self._value_to_bytes(6, 1)
        self.RPMCONST = self._value_to_bytes(60, 1)
        self.ZOOMCONST = self._value_to_bytes(1, 1)
        self._data = {}
        self._num_of_bytes = {}
        self._num_of_bytes['SM'] = 1
        self._num_of_bytes['Azi_dir'] = 1
        self._num_of_bytes['Azi_res'] = 1
        self._num_of_bytes['Azi_RPM'] = 1
        self._num_of_bytes['Azi_steps'] = 4
        self._num_of_bytes['Ele_dir'] = 1
        self._num_of_bytes['Ele_res'] = 1
        self._num_of_bytes['Ele_RPM'] = 1
        self._num_of_bytes['Ele_steps'] = 4
        self._num_of_bytes['EM'] = 1
        # initialising start marker
        self._data['SM'] = 0x24
        # initialising the end marker
        self._data['EM'] = 0x3B
        # Azimuth motor direction
        self._data['Azi_dir'] = self.DIRCONST
        # Azimuth RPM
        self._data['Azi_RPM'] = self.RPMCONST
        # Azimuth steps
        self._data['Azi_steps'] = self.STEPSCONST
        # Elevation motor direction
        self._data['Ele_dir'] = self.DIRCONST
        # Elevation RPM
        self._data['Ele_RPM'] = self.RPMCONST
        # Elevation steps
        self._data['Ele_steps'] = self.STEPSCONST
        # Azimuth motor resolution
        self._data['Azi_res'] = self.RESCONST
        # Elevation motor resolution
        self._data['Ele_res'] = self.RESCONST
        # camera zoom level
        self._camera_zoom = self.ZOOMCONST

    # RPM property
    @property
    def Azi_RPM(self):
        return self._data['Azi_RPM'][0]

    @Azi_RPM.setter
    def Azi_RPM(self, value):
        assert (type(value) != 'int'), "Please make sure that the value passed in is of type <int>"
        if value < 0 or value > 255:
            raise ValueError("RPM value has to be an integer between 0 and 255")
        else:
            self._data['Azi_RPM'] = self._value_to_bytes(value, self._num_of_bytes['Azi_RPM'])

    # Resolution property
    @property
    def Azi_res(self):
        return self._data['Azi_res'][0]

    @Azi_res.setter
    def Azi_res(self, value):
        assert (type(value) != 'int'), "Please make sure that the value passed in is of type <int>"
        if value < 0 or value > 15:
            raise ValueError("The resolution has to be an integer between 0 and 15")
        else:
            self._data['Azi_res'] = self._value_to_bytes(value, self._num_of_bytes['Azi_res'])

    # Motor direction property
    @property
    def Azi_dir(self):
        return self._data['Azi_dir'][0]

    @Azi_dir.setter
    def Azi_dir(self, value):
        assert (type(value) != 'int'), "Please make sure that the value passed in is of type <int>"
        if value not in [0, 1]:
            raise ValueError("value has to be binary, 0 or 1")
        else:
            self._data['Azi_dir'] = self._value_to_bytes(value, self._num_of_bytes['Azi_dir'])

    # Azimuthal steps property
    @property
    def Azi_steps(self):
        return self._data['Azi_steps'][0]

    @Azi_steps.setter
    def Azi_steps(self, value):
        assert (type(value) != 'int'), "Please make sure that the value passed in is of type <int>"
        # TODO implement check
        self._data['Azi_steps'] = self._value_to_bytes(value, self._num_of_bytes['Azi_steps'])

    # Elevation direction property
    @property
    def Ele_dir(self):
        return self._data['Ele_dir'][0]

    @Ele_dir.setter
    def Ele_dir(self, value):
        assert (type(value) != 'int'), "Please make sure that the value passed in is of type <int>"
        if value not in [0, 1]:
            raise ValueError("value has to be binary, 0 or 1")
        else:
            self._data['Ele_dir'] = self._value_to_bytes(value, self._num_of_bytes['Ele_dir'])

    # Elevation resolution property
    @property
    def Ele_res(self):
        return self._data['Ele_res'][0]

    @Ele_res.setter
    def Ele_res(self, value):
        assert (type(value) != 'int'), "Please make sure that the value passed in is of type <int>"
        if value < 0 or value > 15:
            raise ValueError("The resolution has to be an integer between 0 and 15")
        else:
            self._data['Ele_res'] = self._value_to_bytes(value, self._num_of_bytes['Ele_res'])

    # Elevation RPM property
    @property
    def Ele_RPM(self):
        return self._data['Ele_RPM'][0]

    @Ele_RPM.setter
    def Ele_RPM(self, value):
        assert (type(value) != 'int'), "Please make sure that the value passed in is of type <int>"
        if value < 0 or value > 255:
            raise ValueError("RPM value has to be an integer between 0 and 255")
        else:
            self._data['Ele_RPM'] = self._value_to_bytes(value, self._num_of_bytes['Ele_RPM'])

    # Elevation steps property
    @property
    def Ele_steps(self):
        return self._data['Ele_steps']

    @Ele_steps.setter
    def Ele_steps(self, value):
        # TODO implement check
        assert (type(value) != 'int'), "Please make sure that the value passed in is of type <int>"
        self._data['Ele_steps'] = self._value_to_bytes(value, self._num_of_bytes['Ele_steps'])

    @property
    def camera_zoom(self):
        return self._camera_zoom[0]

    @camera_zoom.setter
    def camera_zoom(self, value):
        if 1 <= value <= 28:
            self._camera_zoom = self._value_to_bytes(value, 1)


    @property
    def zoom_command(self):
        command = b'$Z'+bytes(self._camera_zoom)+b';'
        return command

    @property
    def trigger_command(self):
        command = b'$TR;'
        return command

    @property
    def stop_command(self):
        command = b'$SP;'
        return command

    @property
    def start_command(self):
        command = b'$ST;'
        return command

    @property
    def command(self):
        """
        Property that returns a list containing the exact bytes representing
        the packet to be sent
        """
        self._update_state()
        if not self._command_string:
            raise ValueError('Command data has not been updated')
        else:
            return self._command_string

    # internal function that updates the internal state
    def _update_state(self):
        self._command_string = [self._data['SM'],
                                self._data['Azi_dir'][0],
                                self._data['Azi_res'][0],
                                self._data['Azi_RPM'][0],
                                self._data['Azi_steps'][0],
                                self._data['Azi_steps'][1],
                                self._data['Azi_steps'][2],
                                self._data['Azi_steps'][3],
                                self._data['Ele_dir'][0],
                                self._data['Ele_res'][0],
                                self._data['Ele_RPM'][0],
                                self._data['Ele_steps'][0],
                                self._data['Ele_steps'][1],
                                self._data['Ele_steps'][2],
                                self._data['Ele_steps'][3],
                                self._data['EM']]

    def _value_to_bytes(self, value, num_of_bytes):
        """
	@params:
	value - value to be converted
	num_of_bytes - number of bytes that the value has to be represented in
	@return - a list containing byte values(max - 255, min - 0) with length equal to num_of_bytes
        """
        assert (type(value) != 'int'), "Please make sure that the value passed in is of type <int>"
        result = hex(value)[2:]
        assert (len(result) <= 2*num_of_bytes), "Please make sure that the num_of_bytes are enough to support the number represented "  
        result = result.zfill(2*num_of_bytes)
        main_result_list = []
        res_len = len(result)
        for i in range(0, res_len, 2):
            construct = '0x'+result[i:i+2]
            temp = int('0x'+result[i:i+2], 16)
            main_result_list.append(temp)
        return main_result_list

