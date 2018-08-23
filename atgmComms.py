import pdb
import serial as ser
import GenericEvent as GE
import atgmPacket as AP
from threading import Thread, Event

class SerialMedia(object):
    """
    Class description
    """
    # constructor
    def __init__(self, unix_path_to_port, baudrate):
        self.port = unix_path_to_port
        self.baudrate = baudrate
        self._media = ser.Serial(self.port, self.baudrate)
        self.responseEventSig = {'data':None}
        self.responseEvent = GE.GenericEvent(**self.responseEventSig)
        self.steps_responseSig = {'data':None}
        self.steps_responseEvent = GE.GenericEvent(**self.steps_responseSig)
        self.readThread = Thread(target=self._readThread_handler,
                                           name='read thread') 
        self.readThread_stop_event = Event()
        self._response_tally = 32
        self.readThread.start()
        self._is_first_read = True
        self.START_MARKER = b'$'
        self.END_MARKER = b';'
        self._response = b''
        self.send(b'$sc;')

    def send(self, data):
        """
        @params:
            data - is a sequence of bytes
            response_tally - how many bytes is it expecting in response
        @return:
            number of bytes written
        """
        #print("data to be sent: ", data)
        number_of_bytes_sent = self._media.write(data)
        return number_of_bytes_sent

    def _readThread_handler(self):
        while not self.readThread_stop_event._flag:
            response = self._media.read(self._response_tally)
            self._parse(response)
        
   # parses response
    def _parse(self, data):
        """
        @params:
            data - data recieved from remote serial port
        @return:
            None
        """
        # legit code from here
        #print("buffer data existing", self._response)
        #print("new data just recieved: ", data)
        self._response += data
        #print("complete data to be parsed", self._response)
        start_index = 0
        end_index = 0
        while True:
            response_length = len(self._response)
            if response_length == 0:
                break
            if chr(self._response[start_index]) == '$':
                if start_index+1>= response_length:
                    break
                if chr(self._response[start_index+1]) == 'O':
                    # handle OK response
                    end_index = start_index+3
                    if end_index >= response_length:
                        break
                    if chr(self._response[end_index]) == ';':
                        # retrieve data
                        data = self._response[start_index+1:end_index]
                        # fire event
                        self.responseEvent(data=data)
                        # trim the data recieved variable
                        start_index = end_index + 1
                        self._response = self._response[start_index:]
                        start_index = 0
                        continue
                    else:
                        break
                if chr(self._response[start_index+1]) == 'I':
                    # handle Interrupt response
                    end_index = start_index+12
                    if end_index >= response_length:
                        break
                    if chr(self._response[end_index]) == ';':
                        # retrive data
                        data = self._response[start_index+2:end_index]
                        # fire event
                        self.steps_responseEvent(data=data)
                        # trim the data recieved
                        start_index = end_index + 1
                        self._response = self._response[start_index:]
                        start_index=0
                        continue
                    else:
                        break
                if chr(self._response[start_index+1]) == 'C':
                    end_index = start_index+12
                    if end_index >= response_length:
                        break
                    if chr(self._response[end_index]) == ';':
                        # retrieve data
                        data = self._response[start_index+2:end_index]
                        # fire event
                        self.steps_responseEvent(data=data)
                        # trim the data recieved
                        start_index = end_index + 1
                        self._response = self._response[start_index:]
                        start_index=0
                        continue
                    else:
                        break
            else:
                print("start byte is not $")
                break
        return None


    # boolean property to check if the port is open
    @property
    def is_open(self):
        """
        returns the state of the serial media port, whether open or not
        """
        return self._media.is_open
    # release resources
    def release(self):
        self.readThread_stop_event.set()
        self._media.close()

