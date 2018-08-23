# TODO: pipeline detection output into Tracker
# TODO: Implement User defined rectangle for the tracker



import cv2
import FrameEvent as ev
from threading import Thread, Event
import numpy as np
from enum import Enum
#import dlib
from Detector import *
from Tracker_new import *
from enum import Enum
#import ipdb
import pdb

class ImgProMode(Enum):
    VIDEO = 1
    DETECTION = 2
    TRACKING = 3

# class that handles polling of frames and image processing
class ImageProcessor(object):

    # initialization function
    def __init__(self, name=None, mode = ImgProMode.VIDEO):
        self.name = name
        self._video = None
        self.weight_path = "22-Aug-2018-yolo-tank-app-22.h5"
        # frame event
        self.frameEvent = ev.Event_(frame=np.ndarray)
        # tracked frame event
        self.TrackEvent = ev.Event_(rectangle=None, final_image=None)
        # detection frame event
        self.DetectionEvent = ev.Event_(rectangles=None, final_image=None)
        # thread that handles video capture
        self._videoThread = None 
        # declaring a detection thread
        self._detectThread = None 
        # declaring a tracking thread
        self._trackThread = None
        # threading event for video polling
        self._frameloop_stopevent = None
        # threading event for detection
        self._detectloop_stopevent = None
        # threading event for tracking
        self._trackloop_stopevent = None
        # mode of the imageprocessor
        self.mode = mode
        # Tracker
        self.tracker = RE3Tracker()
        # Detector
        self.detector = None

        # few flags
        # flag to maintain the state of tracking: has it started or not
        self.has_tracking_started = False
        # flag to maintain the state of detection: has it starte or not
        self.has_detection_started = False
        # flag to denote whether or not to draw boxes
        self.track_draw_box = None

    # destructor function
    def __del__(self):
        # deletion and release activities
        if self._video is not None:
            self._video.release()
            self._video = None
        self.frameEvent = None
        if self._frameloop_stopevent is not None:
            self._frameloop_stopevent._flag = True
        self._videoThread = None

    # video thread handler
    def frame_thread_handler(self):
        # main polling loop
        while not self._frameloop_stopevent._flag:
            # frame retrieval and checking
            ok, frame = self._video.read()
            if not ok:
                break

            # Video mode
            if self.mode == ImgProMode.VIDEO:
                if self.frameEvent.isSubscribed:
                    self.frameEvent(frame=frame)


        # debug statement
        print("frame polling stopped")
        # re-declaring/initialising the thread
        self._videoThread = Thread(target=self.frame_thread_handler, name="video thread")

        return None

    # Detection thread handler
    def detect_thread_handler(self):
        """Thread handler for detection"""

        while not self._detectloop_stopevent._flag:

            #print("entered detection loop")
            # frame retrieval and checking
            ok, frame = self._video.read()
            if not ok:
                print("frame retrieval not successful")
                break

            # Detection
            if self.mode == ImgProMode.DETECTION:
                if not self.has_detection_started:
                    self.initialize_detector()
                    boxes, image = self.detector.detect(frame)
                    if self.DetectionEvent.isSubscribed:
                        self.DetectionEvent(rectangles=boxes, final_image=image)
                        self.has_detection_started = True
                else:
                    boxes, image = self.detector.detect(frame)
                    if self.DetectionEvent.isSubscribed:
                        self.DetectionEvent(rectangles=boxes, final_image=image)


    def track_thread_handler(self, roi, base_frame):
        """Thread handler for the tracker"""
        while not self._trackloop_stopevent._flag:
            #pdb.set_trace() # BREAKPOINT
            if self.has_tracking_started:
                #frame retrieval and checking
                ok, frame = self._video.read()
                if not ok:
                    break

            # tracking
            if self.mode == ImgProMode.TRACKING:
                if not self.has_tracking_started:
                    self.initialize_tracker(roi, base_frame)
                    self.has_tracking_started = True 
                else:
                    box = self.tracker.update_frame(frame)
                    if self.track_draw_box:
                        cv2.rectangle(frame, (box[0], box[1]), (box[2], box[3]),
                                      (0,0,255), 2)
                    if self.TrackEvent.isSubscribed:
                        self.TrackEvent(rectangle=box, final_image=frame)

    # runs the main frame polling thread
    def run(self, firstrun=False):
        """runs the video frame polling thread"""
        # initialize a stop event that needs to be set to pause/stop the video
        self._frameloop_stopevent = Event()
        self._videoThread = Thread(target=self.frame_thread_handler, name="Video thread")

        if firstrun:
            # initializing video related variables
            if self.name is None:
                self._video = cv2.VideoCapture(0)
                self._video.set(cv2.CAP_PROP_FRAME_WIDTH,720)
                self._video.set(cv2.CAP_PROP_FRAME_HEIGHT,480)
            else:
                self._video = cv2.VideoCapture(self.name)
                self._video.set(cv2.CAP_PROP_FRAME_WIDTH,720)
                self._video.set(cv2.CAP_PROP_FRAME_HEIGHT,480)

        # start the frame polling thread
        self._videoThread.start()

    # runs the detection thread
    def detect_run(self, first_detect):
        """starts the detection thread
        params: first_detect - a boolean flag - denoting first frame to be
                detected"""
        if first_detect:
            # checks whether the video thread is alive, and terminates it if its
            if self.mode == ImgProMode.VIDEO:
                # stops the video thread
                if self._videoThread is not None:
                    self._frameloop_stopevent.set()

            # initializing video related variables
            # if self.name is None:
            #     self._video = cv2.VideoCapture(0)
            # else:
            #     self._video = cv2.VideoCapture(self.name)
            # thread that handles detection
            self._detectThread = Thread(target=self.detect_thread_handler,
                                        name="Detect thread")
            # initialize a stop event that needs to be set to stop detection
            self._detectloop_stopevent = Event()
            # start the thread
            self.mode = ImgProMode.DETECTION
            self._detectThread.start()
        else:
            # initialize thread again
            self._detectThread = Thread(target=self.detect_thread_handler,
                                        name="Detect thread")
            # change mode id it is different
            if self.mode != ImgProMode.DETECTION:
                self._detectloop_stopevent = Event()
            self._detectThread.start()
        return None

    def track_run(self, roi, base_frame, first_track, draw_box):
        """starts the tracking thread
        params: roi - a list of extreme pixel coordinates
                base_frame - np.array consisting of pixel values to be worked
                upon
                first_track - a boolean flag - denoting first frame to be
                Tracked
                draw_box - draws box
        return: None - this function just starts the tracking thread"""
        if first_track:
            # stops the detection thread
            self._detectloop_stopevent.set()
            self.track_draw_box = draw_box

            # thread that handles tracking
            self._trackThread = Thread(target=self.track_thread_handler,
                                       name="Track thread", args=(roi, base_frame))
            # initialize a stop event that needs to be set to stop tracking
            self._trackloop_stopevent = Event()
            # change the mode
            self.mode = ImgProMode.TRACKING
            # start the thread
            self._trackThread.start()
        else:

            # thread that handles tracking
            self._trackThread = Thread(target=self.track_thread_handler,
                                       name="Track thread", args=(roi, base_frame))
            # initialize a stop event that needs to be set to stop tracking
            self._trackloop_stopevent = Event()
            # change mode
            if self.mode != ImgProMode.TRACKING:
                self.mode = ImgProMode.TRACKING
            # start the thread
            self._trackThread.start()
        return None

    # stops/ pauses the video thread
    def stop(self, pause=False):

        # stops the frame thread permanently
        if not pause:

            # send an event to the polling loop to stop polling
            # send an event to the polling loop to stop polling
            if self.mode == ImgProMode.VIDEO:
                self._frameloop_stopevent.set()
            elif self.mode == ImgProMode.DETECTION:
                self._detectloop_stopevent.set()
            elif self.mode == ImgProMode.TRACKING:
                self._trackloop_stopevent.set()
            #self._frameloop_stopevent.set()
            self._video.release()
            self._video = None

        # stops the frame thread but does not delete the video object - mainly for pause
        elif pause:

            # send an event to the polling loop to stop polling
            if self.mode == ImgProMode.VIDEO:
                self._frameloop_stopevent.set()
            elif self.mode == ImgProMode.DETECTION:
                self._detectloop_stopevent.set()
            elif self.mode == ImgProMode.TRACKING:
                self._trackloop_stopevent.set()

    # Mode change
    def change_mode(self, mode):
        """Changes the mode of ImageProcessor to one of the three available in
        the ImgProMode class"""
        self.mode = mode
        return None

    # tracking and detection related functions
    # initialize the tracker
    def initialize_tracker(self, rectangle, frame):

        #self.tracker = RE3Tracker()
        self.tracker.start_tracking(rectangle, frame)
        return None 

    # initialize the detector
    def initialize_detector(self):
        """intializes the yolo detector object"""
        self.detector = YOLODetector()
        self.detector.build_graph()
        self.detector.load_weights(self.weight_path)
       
        

# main function to test the class
def main():
    video_name = '/home/ujjawal/Desktop/demo/tank1.mp4'
    ip = ImageProcessor(video_name)

    return None

if __name__=="__main__":
    #main()
    print(__name__)
