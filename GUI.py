# application flow
# starts with playing the video - user can pause/play the video at will
# user can press detection button
# for tracking, the prior state has to be detection
# while detecting, user has to pause the video, then select tracking 

# TODO: change workflow to detect and track at will
# TODO: allow user given RoI for tracking instead of just tracking from
# detection output
# TODO: add laser module communication support - make it event based

from tkinter import filedialog
import cv2
import tkinter as tk
from tkinter import ttk
import sys
import numpy as np
from PIL import Image
from PIL import ImageTk
import ImageProcessor as ip
import pdb
from PIL.ImageTk import PhotoImage
import FrameEvent as ev
import Comms.SerialCommunication as Comms
import mapper
from enum import Enum

class App_Mode(Enum):
    """enum class to signify which mode to start the application in"""
    LASER_MODE = 1
    DEBUG_MODE = 2

# class that handles displaying image frames(video/jpeg) on a tkinter GUI
class GUI(object):

    # initialization function
    def __init__(self, mode = App_Mode.DEBUG_MODE):
        self.app_mode = mode
        # initializes the window
        self.root = tk.Tk()
        self.root.title('Object Detection and Tracking')
        # some related booleans
        self.first_run = True
        self.first_detect = True
        self.first_track = True
        # name of the video to be played
        self.name = None
        # initializes the image frame - a Label frame inside which the frames will be displayed
        self.imageframe = ttk.LabelFrame(self.root, width=600, height=500)
        self.imageframe.grid(row=0, column=0)
        # initialize and declare a frame that holds all the buttons
        self.buttonframe = ttk.LabelFrame(self.root, width=600, height=100)
        self.buttonframe.grid(row=1, column=0)
        # initialize a few important buttons within the buttonframe
        self.select_video_btn = ttk.Button(self.buttonframe,
                                           text='Select Video', command=self.select_video)
        self.select_video_btn.grid(row=0, column=0)
        self.play_btn = ttk.Button(self.buttonframe, text='Play', command=lambda: self.play(self.first_run))
        self.play_btn.grid(row=0, column=1)
        self.pause_btn = ttk.Button(self.buttonframe, text='Pause', command=self.pause)
        self.pause_btn.grid(row=0, column=2)
        self.detect_btn = ttk.Button(self.buttonframe, text='Detect', command=self.detect)
        self.detect_btn.grid(row=0, column=3)
        self.track_btn = ttk.Button(self.buttonframe, text='Track', command=self.track)
        self.track_btn.grid(row=0, column=4)
        # initialize a label to display the frame
        self.imagelabel = ttk.Label(self.imageframe)
        self.imagelabel.grid(row=0, column=0)
        # mouse events
        self.imagelabel.bind("<Button-1>", self.leftclick)
        # initialize image processing related variables
        self.imageProcessor = ip.ImageProcessor(self.name)
        self.boxes = None  # a list of detection boxes of the latest frame
        # subscribe to different frame events
        self.imageProcessor.frameEvent += self.frame_event_handler
        self.imageProcessor.TrackEvent += self.track_frame_event_handler
        self.imageProcessor.DetectionEvent += self.detect_frame_event_handler
        # detection to tracking
        self.latest_frame = None
        self.boxes = None
        self.tracking_roi = None
        # communication related variables - NOTE: only for tracking
        self.laser_dot = ev.Event_(point=None)
        self.laser_dot += self.laser_dot_handler
        self.laserMedia = None
        # stores the latest laser position
        self.laser_position = [0, 0]
        # mapper to map pixel coordinates to laser coordinates
        self.map = mapper.Mapper()
        self.RES_X = 1024
        self.RES_Y = 768
        self.scale = (self.RES_X, self.RES_Y)
        self.laser_max = (4, 3)
        self.map.set_scale(self.scale, self.laser_max)

    # does a few final cleaning up activities
    def release(self):
        if self.laserMedia is not None:
            self.laserMedia.release()
        self.imageProcessor.frameEvent -= self.frame_event_handler
        self.imageProcessor.TrackEvent -= self.track_frame_event_handler
        self.imageProcessor.DetectionEvent -= self.detect_frame_event_handler
        self.imageProcessor.stop()




    # handler for the detect button - handles detection - NOT IMPLEMENTED
    def detect(self):
        """Starts detection in an already playing video
        params: None
        return: None"""
        if self.first_detect:
            self.imageProcessor.detect_run(self.first_detect)
            self.first_detect = False
        else:
            self.imageProcessor.detect_run(self.first_detect)
        return None

    # handler for file dialogue
    def select_video(self):
        """selects the relevant path for video to be played"""
        self.imageProcessor.name = tk.filedialog.askopenfilename()
        return None

    # handler for the track button - handles tracking - NOT IMPLEMENTED
    def track(self):
        """Starts tracking the selected RoI
        params: None
        return: None"""
        if self.first_track:
            if self.app_mode == App_Mode.DEBUG_MODE:
                self.imageProcessor.track_run(self.tracking_roi,
                                              self.latest_frame,
                                              self.first_track, True)
            elif self.app_mode == App_Mode.LASER_MODE:
                self.laserMedia = Comms.LaserModule()
                self.imageProcessor.track_run(self.tracking_roi,
                                              self.latest_frame,
                                              self.first_track,False)
            self.first_track = False
        else:
            self.imageProcessor.track_run(self.tracking_roi, self.latest_frame,
                                         self.first_track) 

        return None

    # handler for play button
    def play(self, first_run):
        if first_run:
            # run the polling thread
            self.imageProcessor.run(first_run)
            # switching the first run flag
            self.first_run = False
        else:
            # plays the video stream
            self.imageProcessor.run()
        return None

    # handler for the pause button
    def pause(self):
        # pause the video
        self.imageProcessor.stop(pause=True)
        return None

    # handler for the frame event
    def frame_event_handler(self, frame):
        # switch to RGB format
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        # make it PIL ImageTk compatible
        image = Image.fromarray(image)
        # make it imgtk compatible
        image = ImageTk.PhotoImage(image)
        # store the image in the label
        self.imagelabel.imgtk = image
        # configure the image to the corresponding size
        self.imagelabel.configure(image=image)
        # store the reference to the image so that Python's gc doesn't erase the image
        self.imagelabel.image = image
        return None


    # handler of track frame events
    def track_frame_event_handler(self, rectangle, final_image):
        """frame handler for track frames
        params: rectangle - a list denoting the RoI being tracked
                final_image - a np.array() - denoting the final frame to drawn
        Return: None"""
        # relay laser position
        point = self.find_center(rectangle)
        # raise laser event to relay laser point
        if self.app_mode == App_Mode.LASER_MODE:
            self.laser_dot(point=point)
        # switch to RGB format
        image = cv2.cvtColor(final_image, cv2.COLOR_BGR2RGB)
        # make it PIL ImageTk compatible
        image = Image.fromarray(image)
        # make it imgtk compatible
        image = ImageTk.PhotoImage(image)
        # store the image in the label
        self.imagelabel.imgtk = image
        # configure the image to the corresponding size
        self.imagelabel.configure(image=image)
        # store the reference to the image so that Python's gc doesn't erase the image
        self.imagelabel.image = image
        return None

    # handler of detection frame events
    def detect_frame_event_handler(self, rectangles=None, final_image=None):
        """frame handler for track frames
        params: rectangle denoting the RoI being tracked
        Return: None"""
        # possible detection to tracking
        self.latest_frame = final_image
        self.boxes = rectangles
        # switch to RGB format
        image = cv2.cvtColor(final_image, cv2.COLOR_BGR2RGB)
        # make it PIL ImageTk compatible
        image = Image.fromarray(image)
        # make it imgtk compatible
        image = ImageTk.PhotoImage(image)
        # store the image in the label
        self.imagelabel.imgtk = image
        # configure the image to the corresponding size
        self.imagelabel.configure(image=image)
        # store the reference to the image so that Python's gc doesn't erase the image
        self.imagelabel.image = image
        return None

    def run(self):
        # run the GUI
        self.root.mainloop()
        return None

    def leftclick(self, event):
        """mouse leftclick event handler, selects the box to be tracked"""
        x = event.x
        y = event.y
        point = (x, y)
        roi_list = self.boxes
        for roi in roi_list:
            if self.point_in_box(point, roi):
                self.tracking_roi = roi
        return None

    def point_in_box(self, point, box):
        """ returns the clicked region of interest
        params: point - a tuple consisting of the mouseevent pixel coordinate
        return: True/False - a boolean"""
        (x, y) = point
        if (x>box[0] and x<box[2] and y>box[1] and y<box[3]):
            return True
        else:
            return False


    def find_center(self, rectangle):
        """finds the center of a given rectangle
        params: rectangle - a list [xmin, ymin, xmax, ymax]
        return: point - a tuple (x, y) corresponding to the center of the rectangle"""
        xmin = rectangle[0]
        ymin = rectangle[1]
        xmax = rectangle[2]
        ymax = rectangle[3]

        x = xmin+((int)(xmax-xmin)/2)
        y = ymin+((int)(ymax-ymin)/2)
        point = (x, y)
        return point

    def laser_dot_handler(self, point):
        """handler for the laser dot
        params: point - a tuple containing the coordinates of the laser dot
        return: None"""
        (x, y) = point
        laser_point = self.map.get_laser_point(point)
        x = laser_point[0]
        y = laser_point[1]
        negative_laser_point = [-x, -y]
        if  self.laser_position != negative_laser_point:
            self.laser_position = self.laserMedia.move_XY(self.laser_position,
                                                          laser_point[0], laser_point[1])

        return None


def main():
    video = GUI(App_Mode.LASER_MODE)
    video.run()
    video.release()
    return None

if __name__ == "__main__":
    main()
