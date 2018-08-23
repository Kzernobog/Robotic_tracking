from AbstractTracker import *
#import dlib
from enum import Enum
#import ipdb
import pdb
import cv2
import argparse
import glob
import numpy as np
import os
import time
import sys
#from ImageProcessor import *

basedir = os.path.dirname(__file__)
sys.path.append(os.path.abspath(os.path.join(basedir, os.path.pardir)))
from tracker import re3_tracker

from re3_utils.util import drawing
from re3_utils.util import bb_util
from re3_utils.util import im_util

from constants import OUTPUT_WIDTH
from constants import OUTPUT_HEIGHT
from constants import PADDING

np.set_printoptions(precision=6)
np.set_printoptions(suppress=True)

boxToDraw = np.zeros(4)
initialize = False

class TrackerType(Enum):
    DLIB = 1
    ROLO = 2
    DEEPSORT = 3
    TRACK2DETECT = 4
    KLT = 5
    GOTURN = 6
    RE3 = 7



# class that handles tracking computation
class DLIBTracker(AbstractTracker):

    # Constuctor
    def __init__(self, tracker_type=TrackerType.DLIB): 
        # initializing the type of tracker to be used
        self.tracker_type = tracker_type
        self.tracker = None

    # initialize the tracker
    def start_tracking(self, rectangle,frame):
        """Initializes and starts the dlib tracker
        params: rectangle - a list [xmin, ymin, xmax, ymax]
                frame - np.array() initial image frame
        return: None"""
        if self.tracker_type == TrackerType.DLIB:
            self.tracker = dlib.correlation_tracker()
            dlib_rect = dlib.rectangle(*rectangle)
            self.tracker.start_track(frame, dlib_rect)
            return None

    # update the tracker
    def update_frame(self, frame):
        """Updates the tracked rectangle
        params: frame - np.array() image frame used for computation
        return: rectangle - a list [xmin, ymin, xmax, ymax]"""
        self.tracker.update(frame)
        track_rect = self.tracker.get_position()
        xmin = int(track_rect.left())
        ymin = int(track_rect.top())
        xmax = int(track_rect.right())
        ymax = int(track_rect.bottom())
        result = [xmin,ymin,xmax,ymax]
        return result 


class RE3Tracker(AbstractTracker):

    # Constuctor
    def __init__(self, tracker_type=TrackerType.RE3): 
        # initializing the type of tracker to be used
        #self.tracker = re3_tracker.Re3Tracker()
        self.tracker_type = tracker_type
        self.tracker = re3_tracker.Re3Tracker()
    # initialize the tracker
    def start_tracking(self, rectangle,frame):
        """Initializes and starts the dlib tracker
        params: rectangle - a list [xmin, ymin, xmax, ymax]
                frame - np.array() initial image frame
        return: None"""
        if self.tracker_type == TrackerType.RE3:
            #self.tracker = re3_tracker.Re3Tracker()
            #dlib_rect = dlib.rectangle(*rectangle)
            re3_rect = rectangle
            self.tracker.track('webcam',frame, re3_rect)
            return None

    # update the tracker
    def update_frame(self, frame):
        """Updates the tracked rectangle
        params: frame - np.array() image frame used for computation
        return: rectangle - a list [xmin, ymin, xmax, ymax]"""
        boxToDraw = self.tracker.track('webcam',frame)
        return boxToDraw 


