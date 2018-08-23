# TODO: 
    # handle electronics response after a command is sent
    # add up total steps that the turret has moved
    # figure out wheh to break the while loop  
import atgmData as ad
import atgmComms as ac
from threading import Thread, Event
import time
import threading


class ATGMCalibrator(object):
    """
    Class description
    This class implements the calibration funcitonality for the ATGM turret.
    It makes a note of maximum physical movement capability of the turret and
    then proceeds to set software limits.
    """
    def __init__(self, port, baudrate):
        self.left_movement = ad.ATGMData()
        self.right_movement = ad.ATGMData()
        self.top_movement = ad.ATGMData()
        self.bottom_movement = ad.ATGMData()
        self._construct_calibration_packets()
        self._atgmMedia = ac.SerialMedia(port, baudrate)
        self._atgmMedia.responseEvent += self._responseHandler
        self._worldCalibThread = None
        self._scenarioCalibThread = None
        self._world_loop_stopevent = None
        self._scenario_loop_stopevent = None
        self.number_left_steps = None
        self.number_right_steps = None
        self.number_top_steps = None
        self.number_botton_steps = None

    def _world_thread_handler(self):
        while not self._world_loop_stopevent._flag:
            self._atgmMedia.send(self.left_movement.command, 14)


    def world_start(self):
        self._world_loop_stopevent = Event()
        self._worldCalibThread = Thread(target=self._world_thread_handler,name='world calibration thread')
        self.worldCalibThread.start()

    def word_stop(self):
        self._world_loop_stopevent.set()

    def scenario_start(self):
        self._scenario_loop_stopevent = Event()
        self._scenarioCalibThread = Thread(target=self._scenario_thread_handler, name='scenario calibration thread')
        self._scenarioCalibThread.start()


    def _scenario_thread_handler(self):
        while not self._scenario_loop_stopevent._flag:
            self._atgmMedia.send(self.left_movement.command, 14)



    def _responseHandler(self, data):
        pass


    def _construct_calibration_packets(self):
        # left movement
        self.left_movement.Azi_dir = 0x01
        self.left_movement.Azi_res = 0x06
        self.left_movement.Azi_RPM = 0x4B
        self.left_movement.Azi_steps = 0x05
        self.left_movement.Ele_dir = 0x00
        self.left_movement.Ele_res = 0x00
        self.left_movement.Ele_RPM = 0x00
        self.left_movement.Ele_steps = 0x00

        # right movement
        self.right_movement.Azi_dir = 0x00
        self.right_movement.Azi_res = 0x06
        self.right_movement.Azi_RPM = 0x4B
        self.right_movement.Azi_steps = 0x05
        self.right_movement.Ele_dir = 0x00
        self.right_movement.Ele_res = 0x00
        self.right_movement.Ele_RPM = 0x00
        self.right_movement.Ele_steps = 0x00

        # top movement
        self.top_movement.Azi_dir = 0x00
        self.top_movement.Azi_res = 0x00
        self.top_movement.Azi_RPM = 0x00
        self.top_movement.Azi_steps = 0x00
        self.top_movement.Ele_dir = 0x01
        self.top_movement.Ele_res = 0x06
        self.top_movement.Ele_RPM = 0x4B
        self.top_movement.Ele_steps = 0x05

        # bottom movement
        self.bottom_movement.Azi_dir = 0x00
        self.bottom_movement.Azi_res = 0x00
        self.bottom_movement.Azi_RPM = 0x00
        self.bottom_movement.Azi_steps = 0x00
        self.bottom_movement.Ele_dir = 0x00
        self.bottom_movement.Ele_res = 0x06
        self.bottom_movement.Ele_RPM = 0x4B
        self.bottom_movement.Ele_steps = 0x05

    @property
    def left_movement(self):
        return self.left_movement.command

    @property
    def right_movement(self):
        return self.right_movement.command

    @property
    def top_movement(self):
        return self.top_movement.command

    @property
    def bottom_movement(self):
        return self.bottom_movement.command

