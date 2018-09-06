import time
import struct
import pdb
from threading import Thread
import threading
import atgmData as ad
import atgmCalibration as calibrator
import hexcompute as hc
import string
import serial as sl
import tkinter as tk
from tkinter import ttk
from tkinter import scrolledtext as sct
import os
import atgmComms as AC
import turret_control as tc
from tkinter import messagebox as msg
import atgmState as state
import ImageProcessor_new as ip
from PIL import Image
from PIL import ImageTk
from PIL.ImageTk import PhotoImage
import cv2
import sys

class Atgm_Diagnostic_GUI(object):
    
    def __init__(self):
        # some constants
        self.UP = 0
        self.RIGHT = 0
        # declare a window
        self.root = tk.Tk()
        self.root.protocol("WM_DELETE_WINDOW", self._exit)
        self.root.title("Serial Diagnostics")
        self.width = 720
        self.height = 480

        # TODO: Determine where auto mode must be turned off
        # whether in auto mode or keyboard mode
        self.auto_mode = True

        self._crosshair_image = Image.open("red_crosshair.png")

        # if GUI is being run on a macOSX
        if self.root.tk.call('tk', 'windowingsystem') == 'aqua':
            s = ttk.Style()
            s.configure('TNotebook.Tab', padding=(12, 8, 12, 0))

        # initialize tab control
        self._init_tabControl()

        # initialize the serial media tab
        #self._init_serialTab()

        # initialize atgm configuration tab
        #self._init_atgmConfigTab()

        # initialize atgm command tab
        self._init_atgm_command()

        # Communication related variables
        self._atgmMedia = None
        # a hex converter class
        self.hex_compute = hc.Hex_Computer()

        # threading related variables
        self._worldCalibThread = None
        self._scenarioCalibThread = None

        self._imageProcessor = ip.ImageProcessor()
        self._imageProcessor.DetectionEvent += self._detection_event_handler
        self._imageProcessor.TrackEvent += self._track_event_handler
        self._imageProcessor.frameEvent += self._frame_event_handler

        # class related booleans
        self._first_detect = True
        self._first_run = True
        self._first_track = True
        self._keyboard_initialised = False

        # detection related variable
        self.latest_frame = None
        self.boxes = None

        # atgm data container class
        self.atgmCommand_data = ad.ATGMData()

        # variable that keep a record of the current state
        self._atgmState = state.ATGMState()
        # self._imageProcessor.run(self._first_run)
        # self._first_run = False

        # create a turret control object
        self.turret_control = tc.Turret_control()


    def _init_serialTab(self):

        # Serial Port Tab

        # declare a holder frame
        self.frame = ttk.LabelFrame(self.serialportTab, text='Configure:', width=self.width, height=self.height)
        self.frame.grid(row=0, column=0)

        # declare a text entry to take the port
        # try and auto populate this 
        self.device_text = tk.StringVar()
        self.device_combobox = ttk.Combobox(self.frame, width=12, textvariable=self.device_text, state='readonly')
        self.device_combobox['values'] = self.__populateDeviceCombobox__()
        self.device_combobox.grid(row=1, column=0)
        self.device_label = ttk.Label(self.frame, text='Select port:')
        self.device_label.grid(row=0, column=0)
        # self.device_text= tk.StringVar()
        # self.textbox = ttk.Entry(self.frame, textvariable=self.device_text)
        # self.textbox.grid(row=0, column=0)
        # combobox for baudrate
        self.baudrate = tk.IntVar()
        self.baudrate_combobox = ttk.Combobox(self.frame, width=12, textvariable=self.baudrate, state='readonly')
        self.baudrate_combobox['values'] = (4800, 9600, 19200, 38400, 57600, 76800, 460800, 115200)
        self.baudrate_combobox.grid(row=1, column=1)
        self.baudrate_label = ttk.Label(self.frame, text='Baudrate:')
        self.baudrate_label.grid(row=0, column=1)
        # self.button = ttk.Button(self.frame, text='Connect', command=self.connect)
        # self.button.grid(row=0,column=2)
        # combobox for parity
        self.parity = tk.StringVar()
        self.parity_combobox = ttk.Combobox(self.frame, width=12,textvariable=self.parity, state='readonly')
        self.parity_combobox['values'] = ('none', 'even', 'odd')
        self.parity_combobox.grid(row=1, column=2)
        self.parity_label = ttk.Label(self.frame, text='Parity:')
        self.parity_label.grid(row=0, column=2)
        # combobox for bits
        self.bits = tk.IntVar()
        self.bits_combobox = ttk.Combobox(self.frame, width=12,textvariable=self.bits, state='readonly')
        self.bits_combobox['values'] = (8, 7)
        self.bits_combobox.grid(row=1, column=3)
        self.bits_label = ttk.Label(self.frame, text='Bits:')
        self.bits_label.grid(row=0, column=3)
        # combobox for stopbits
        self.stopbits = tk.IntVar()
        self.stopbits_combobox = ttk.Combobox(self.frame, width=12,textvariable=self.stopbits, state='readonly')
        self.stopbits_combobox['values'] = (1,2)
        self.stopbits_combobox.grid(row=3, column=0)
        self.stopbits_label = ttk.Label(self.frame, text='Stop Bits:')
        self.stopbits_label.grid(row=2, column=0)

        # radio buttons for either hex ot ascii command entries
        self.hexradvar = tk.StringVar()
        self.hexradvar.set("ascii")
        self.hexRadButton = tk.Radiobutton(self.frame, text="Hex",
                                           variable=self.hexradvar,
                                           value='hex', command=None)
        self.hexRadButton.grid(row=3, column=1)
        self.asciiRadButton = tk.Radiobutton(self.frame, text="Ascii",
                                             variable=self.hexradvar,
                                             value='ascii', command=None)
        self.asciiRadButton.grid(row=3, column=2)

        # open port button
        self.openButton = ttk.Button(self.frame, text='Open Port', command=self.openport)
        self.openButton.grid(row=3, column=3, sticky='WE')

        # labelframe for I/O echo
        # self.IOframe = ttk.LabelFrame(self.root, text='I/O Echo:')
        # self.IOframe.grid(row=1, column=0) 

        # scrolled text for serial input and output echo
        self.scrolled_text = tk.StringVar()
        self.echoScrolledTextBox = sct.ScrolledText(self.frame, wrap=tk.WORD)
        # debug print
        #self.echoScrolledTextBox.insert(2.0, 'Thaswassup')
        self.echoScrolledTextBox.grid(row=4, column=0, sticky='WE', columnspan=4)

        # send button
        self.sendButton = ttk.Button(self.frame, text='Send', command=self.send)
        self.sendButton.grid(row=5, column=3, sticky='WE')

        # Command textbox
        self.command = tk.StringVar()
        self.command_entered = ttk.Entry(self.frame, textvariable=self.command)
        self.command_entered.grid(row=5, column=0, sticky='WE', columnspan=3)
        self.root.resizable(False, False)

    def _init_tabControl(self):

    # declare 3 different tabs and name them
        # tab for serial comms
        self.tabcontrol = ttk.Notebook(self.root)

        # serial tab

        #self.serialportTab = ttk.Frame(self.tabcontrol)
        #self.tabcontrol.add(self.serialportTab, text='Serial Comms')
        # tab for basic commands
        self.atgmBasicCommandsTab = ttk.Frame(self.tabcontrol)
        self.tabcontrol.add(self.atgmBasicCommandsTab, text='ATGM Commands')
        # tab for Configuration
        #self.atgmconfigTab = ttk.Frame(self.tabcontrol)
        #self.tabcontrol.add(self.atgmconfigTab, text='ATGM Configuration')

        self.tabcontrol.pack(expand=1, fill='both')

    def _init_atgm_command(self):
        self.atgm_command_frame = ttk.LabelFrame(self.atgmBasicCommandsTab, text='Commands:', width=self.width, height=self.height)
        self.atgm_command_frame.grid(row=0, column=0)

        # self.atgm_image_frame = ttk.LabelFrame(self.atgmBasicCommandsTab, text='Feed', width=self.width, height=self.height)
        # self.atgm_image_frame.grid(row=1, column=0)

        # self.atgm_command_config_frame = ttk.LabelFrame(self.atgmBasicCommandsTab, text='Configuration', width=self.width, height=self.height)
        # self.atgm_command_config_frame.grid(row=0, column=1)

        # self.atgmCommand_elevation_reset_button = ttk.Button(self.atgm_command_config_frame, text='Reset Elevation', command=self._reset_elevation)
        # self.atgmCommand_elevation_reset_button.grid(row=0, column=0)

        # self.atgmCommand_pixel_step_estimator_button = ttk.Button(self.atgm_command_config_frame, text='Estimate ratio', command=self._estimate_ratio)
        # self.atgmCommand_pixel_step_estimator_button.grid(row=1, column=0)



        # self.atgm_imagelabel = ttk.Label(self.atgm_image_frame)
        # self.atgm_imagelabel.grid(row=0, column=0) 
        # self.atgm_imagelabel.bind("<Button-1>", self.leftclick)
        # self.tracking_roi = None

        self.atgm_imagelabel = ttk.Label(self.atgm_command_frame)
        self.atgm_imagelabel.grid(row=7, column=0, columnspan=4) 
        self.atgm_imagelabel.bind("<Button-1>", self.leftclick)
        self.tracking_roi = None
        
        # device to connect to
        self.atgmCommand_device_text = tk.StringVar()
        self.atgmCommand_device_combobox = ttk.Combobox(self.atgm_command_frame,
                                                       width=12, textvariable=self.atgmCommand_device_text,
                                                       state='readonly')
        self.atgmCommand_device_combobox['values'] = self.__populateDeviceCombobox__()
        self.atgmCommand_device_combobox.grid(row=1, column=0)
        self.atgmCommand_device_label = ttk.Label(self.atgm_command_frame,
                                                  text='Select port:')
        self.atgmCommand_device_label.grid(row=0, column=0)

        # azimuth combo box
        self.atgmCommand_azi_dir_text = tk.StringVar()
        self.atgmCommand_azi_dir_combobox = ttk.Combobox(self.atgm_command_frame, width=12,
                                                         textvariable=self.atgmCommand_azi_dir_text,
                                                         state='readonly')
        self.atgmCommand_azi_dir_combobox['values'] = ('Right', 'Left')
        self.atgmCommand_azi_dir_combobox.grid(row=3, column=0)
        self.atgmCommand_azi_dir_label = ttk.Label(self.atgm_command_frame,
                                                   text='Azimuth Direction')
        self.atgmCommand_azi_dir_label.grid(row=2, column=0)
        
        # elevation combobox
        self.atgmCommand_ele_dir_text = tk.StringVar()
        self.atgmCommand_ele_dir_combobox = ttk.Combobox(self.atgm_command_frame, width=12, textvariable=self.atgmCommand_ele_dir_text, state='readonly')
        self.atgmCommand_ele_dir_combobox['values'] = ('Up', 'Down')
        self.atgmCommand_ele_dir_combobox.grid(row=3, column=1)
        self.atgmCommand_ele_dir_label = ttk.Label(self.atgm_command_frame,
                                                     text='Elevation Direction')
        self.atgmCommand_ele_dir_label.grid(row=2, column=1)

        # Azimuth steps
        self.atgmCommand_azi_steps_text = tk.StringVar()
        self.atgmCommand_azi_steps_textbox = ttk.Entry(self.atgm_command_frame,
                                                      textvariable=self.atgmCommand_azi_steps_text)
        self.atgmCommand_azi_steps_textbox.grid(row=3, column=2)
        self.atgmCommand_azi_steps_label = ttk.Label(self.atgm_command_frame,
                                                     text='Azimuth steps')
        self.atgmCommand_azi_steps_label.grid(row=2, column=2)

        # elevation steps
        self.atgmCommand_ele_steps_text = tk.StringVar()
        self.atgmCommand_ele_steps_textbox = ttk.Entry(self.atgm_command_frame,
                                                      textvariable=self.atgmCommand_ele_steps_text)
        self.atgmCommand_ele_steps_textbox.grid(row=3, column=3)
        self.atgmCommand_ele_steps_label = ttk.Label(self.atgm_command_frame,
                                                     text='Elevation steps')
        self.atgmCommand_ele_steps_label.grid(row=2, column=3)

        # azimuth resolution
        self.atgmCommand_azi_res_text = tk.IntVar()
        self.atgmCommand_azi_res_combobox =ttk.Combobox(self.atgm_command_frame, width=12,
                                                        textvariable=self.atgmCommand_azi_res_text, state='readonly')
        self.atgmCommand_azi_res_combobox['values'] = (0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15)
        self.atgmCommand_azi_res_combobox.grid(row=5, column=0)
        self.atgmCommand_azi_res_label = ttk.Label(self.atgm_command_frame,
                                                   text='Azimuth resolution')
        self.atgmCommand_azi_res_label.grid(row=4, column=0)

        # elevation resolution
        self.atgmCommand_ele_res_text = tk.IntVar()
        self.atgmCommand_ele_res_combobox =ttk.Combobox(self.atgm_command_frame, width=12,
                                                        textvariable=self.atgmCommand_ele_res_text, state='readonly')
        self.atgmCommand_ele_res_combobox['values'] = (0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15)
        self.atgmCommand_ele_res_combobox.grid(row=5, column=1)
        self.atgmCommand_ele_res_label = ttk.Label(self.atgm_command_frame,
                                                   text='Elevation resolution')
        self.atgmCommand_ele_res_label.grid(row=4, column=1)

        # RPM of azimuth motor
        self.atgmCommand_azi_RPM_text = tk.StringVar()
        self.atgmCommand_azi_RPM_textbox = ttk.Entry(self.atgm_command_frame,
                                                     textvariable=self.atgmCommand_azi_RPM_text)
        self.atgmCommand_azi_RPM_textbox.grid(row=5, column=2)
        self.atgmCommand_azi_RPM_label = ttk.Label(self.atgm_command_frame,
                                                   text='Azimuth RPM')
        self.atgmCommand_azi_RPM_label.grid(row=4, column=2)

        # RPM of elevation motor
        self.atgmCommand_ele_RPM_text = tk.StringVar()
        self.atgmCommand_ele_RPM_textbox = ttk.Entry(self.atgm_command_frame,
                                                     textvariable=self.atgmCommand_ele_RPM_text)
        self.atgmCommand_ele_RPM_textbox.grid(row=5, column=3)
        self.atgmCommand_ele_RPM_label = ttk.Label(self.atgm_command_frame,
                                                   text='Elevation RPM')
        self.atgmCommand_ele_RPM_label.grid(row=4, column=3)

        # send button
        self.atgmCommand_send_button = ttk.Button(self.atgm_command_frame,
                                                  text='send',
                                                  command=self.send_atgmCommand)
        self.atgmCommand_send_button.grid(row=6, column=4)

        self.atgmCommand_feed_button = ttk.Button(self.atgm_command_frame, text='start feed', command=self._start_video_feed)
        self.atgmCommand_feed_button.grid(row=6, column=2)

        self.atgmCommand_feed_button = ttk.Button(self.atgm_command_frame, text='stop everything', command=self._image_processor_clean_up)
        self.atgmCommand_feed_button.grid(row=6, column=3)

        # open port button
        self.atgmCommand_openPort_button = ttk.Button(self.atgm_command_frame,
                                                     text='Open Port',
                                                     command=self.openport_atgmCommand)
        self.atgmCommand_openPort_button.grid(row=1, column=3)

        self.atgmCommand_openPort_label = ttk.Label(self.atgm_command_frame,
                                                   text='Port inactive')
        self.atgmCommand_openPort_label.grid(row=0, column=3)

        # choose keyboard mode
        self.keyboard_radvar = tk.IntVar()
        self.keyboard_radvar.set(2)
        self.keyboard_radButton = tk.Radiobutton(self.atgm_command_frame,
                                                 text='Keyboard Mode',
                                                 variable=self.keyboard_radvar,
                                                 value = 1,
                                                 command=self._init_keyboard,
                                                 relief=tk.FLAT)
        self.keyboard_radButton.grid(row=6, column=0)
        self.normal_mode_radButton = tk.Radiobutton(self.atgm_command_frame,
                                                    text='Normal Mode',
                                                   variable=self.keyboard_radvar,
                                                   value=2,
                                                   command=self._deinit_keyboard,
                                                   relief=tk.FLAT)
        self.normal_mode_radButton.grid(row=6, column=1)

        # remove after debugging
        #self.atgmCommand_elevation_steps_label = ttk.Label(self.atgm_command_frame, text='Elevation steps: ')
        #self.atgmCommand_elevation_steps_label.grid(row=6, column=2)

    # esimates the pixel per step ratio for azimuth and elevation
    def _estimate_ratio(self):
        if not self._keyboard_initialised:
            self.atgm_command_frame.bind("<Key>", self._use_keyboard)
            self._keyboard_initialised = True
        self.atgm_command_config_frame.focus_set()

    def _start_video_feed(self):
        self._imageProcessor.run(self._first_run)
        self._first_run = False

    def _reset_elevation(self):
        pass

    # frame event handler
    def _detection_event_handler(self, rectangles=None, final_image=None):
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
        self.atgm_imagelabel.imgtk = image
        # configure the image to the corresponding size
        self.atgm_imagelabel.configure(image=image)
        # store the reference to the image so that Python's gc doesn't erase the image
        self.atgm_imagelabel.image = image
        return None

    # handler for the frame event
    def _frame_event_handler(self, frame):
        try:
            # switch to RGB format
            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            print("displaying frame")
            # make it PIL ImageTk compatible
            image = Image.fromarray(image)
            # make it imgtk compatible
            print("displaying frame")
            image = ImageTk.PhotoImage(image)
            # store the image in the label
            print("displaying frame")
            self.atgm_imagelabel.imgtk = image
            # configure the image to the corresponding size
            self.atgm_imagelabel.configure(image=image)
            # store the reference to the image so that Python's gc doesn't erase the image
            self.atgm_imagelabel.image = image
            print("displayed frame")
            return None
        except:
            print("frame recieved exception")
            return None


    # handler of track frame events
    def _track_event_handler(self, rectangle, final_image):
        """frame handler for track frames
        params: rectangle - a list denoting the RoI being tracked
                final_image - a np.array() - denoting the final frame to drawn
        Return: None"""
        # relay laser position
        point = self.find_center(rectangle)
        x, y = point
        #print("tracking center: ", x, y)
        # construct and send the command to move atgm based on the tank position (x, y)
        if self.auto_mode:
            self._send_move_command(x, y)

        # switch to RGB format
        image = cv2.cvtColor(final_image, cv2.COLOR_BGR2RGB)
        # make it PIL ImageTk compatible
        image = Image.fromarray(image)
        # crosshair overlay
        image = self._crosshair_overlay(image, self._crosshair_image)
        # make it imgtk compatible
        image = ImageTk.PhotoImage(image)
        # store the image in the label
        self.atgm_imagelabel.imgtk = image
        # configure the image to the corresponding size
        self.atgm_imagelabel.configure(image=image)
        # store the reference to the image so that Python's gc doesn't erase the image
        self.atgm_imagelabel.image = image

        # comms related
        # retrieve azimuth and elevationb steps
        # update the necessaryt object that handles construction of command
        # then send the command
        return None
    def _crosshair_overlay(self, base_img, crosshair_img, crosshair_size = (48, 48)):
        base_img = base_img.copy()
        crosshair_img = crosshair_img.resize(crosshair_size)
        crosshair_position = (base_img.width//2 - crosshair_size[0]//2
                             , base_img.height//2 - crosshair_size[1]//2)
        base_img.paste(crosshair_img, crosshair_position, crosshair_img)
        return base_img

    def _send_move_command(self, x, y):
        zoom_level = self.atgmCommand_data.camera_zoom
        number_of_azimuth_steps, number_of_elevation_steps = self.turret_control.get_azimuth_elevation((x, y), zoom_level)

        self.atgmCommand_data.Ele_dir = 1 * (number_of_elevation_steps > 0)
        self.atgmCommand_data.Ele_steps = abs(number_of_elevation_steps)
        self.atgmCommand_data.Azi_dir = 1 * (number_of_azimuth_steps < 0)
        self.atgmCommand_data.Azi_steps = abs(number_of_azimuth_steps)
        self._atgmMedia.send(self.atgmCommand_data.command)

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

    # initialise keyboard usage
    def _init_keyboard(self):
        self.atgm_command_frame.bind("<Key>", self._use_keyboard)
        self.atgm_command_frame.focus_set()

        

    # switch off keyboard usage
    def _deinit_keyboard(self):
        self.atgm_command_frame.unbind("<Key>")
        self.atgmCommand_send_button.configure(state='NORMAL')

    # keyboard event handler
    # def _use_keyboard(self, event):
    #     print(event.keysym+" pressed")
    #     print("time "+time.time())

    def _use_keyboard(self, event):
        if event.keysym == 'Up':
            self.atgmCommand_data.Ele_dir = 0
            self.atgmCommand_data.Ele_steps = 8000

            self.atgmCommand_data.Azi_dir = 0
            self.atgmCommand_data.Azi_steps = 0
            self._atgmMedia.send(self.atgmCommand_data.command)
            return
        if event.keysym == 'Down':
            self.atgmCommand_data.Ele_dir = 1
            self.atgmCommand_data.Ele_steps = 8000
            self.atgmCommand_data.Azi_dir = 0
            self.atgmCommand_data.Azi_steps = 0
            self._atgmMedia.send(self.atgmCommand_data.command)
            return
        if event.keysym == 'Left':
            self.atgmCommand_data.Ele_dir = 0
            self.atgmCommand_data.Ele_steps = 0
            self.atgmCommand_data.Azi_dir = 1
            self.atgmCommand_data.Azi_steps = 8000
            self._atgmMedia.send(self.atgmCommand_data.command)
            return
        if event.keysym == 'Right':
            self.atgmCommand_data.Ele_dir = 1
            self.atgmCommand_data.Ele_steps = 0
            self.atgmCommand_data.Azi_dir = 0
            self.atgmCommand_data.Azi_steps = 8000
            self._atgmMedia.send(self.atgmCommand_data.command)
            return
        if event.char == 'w':
            if 0 < self.atgmCommand_data.Azi_RPM < 255:
                self.atgmCommand_data.Azi_RPM += 1
                self._atgmMedia.send(self.atgmCommand_data.command)
            return
        if event.char == 's':
            if 0 < self.atgmCommand_data.Azi_RPM < 255:
                self.atgmCommand_data.Azi_RPM -= 1
                self._atgmMedia.send(self.atgmCommand_data.command)
            return
        if event.char == 'o':
            if 0 < self.atgmCommand_data.Ele_RPM < 255:
                self.atgmCommand_data.Ele_RPM += 1
                self._atgmMedia.send(self.atgmCommand_data.command)
            return
        if event.char == 'l': 
            if 0 < self.atgmCommand_data.Ele_RPM < 255:
                self.atgmCommand_data.Ele_RPM -= 1
                self._atgmMedia.send(self.atgmCommand_data.command)
            return
        if event.char == 'z':
            self.atgmCommand_data.camera_zoom += 1
            self._atgmMedia.send(self.atgmCommand_data.zoom_command)
        if event.char == 'x':
            self.atgmCommand_data.camera_zoom -= 1
            self._atgmMedia.send(self.atgmCommand_data.zoom_command)
        if event.char == 't':
            self._atgmMedia.send(self.atgmCommand_data.trigger_command)
        if event.char == 'r':
            self._atgmState.reset()
        if event.char == 'f':
            self._atgmMedia.send(self.atgmCommand_data.stop_command)
        if event.char == 'p':
            self._atgmMedia.send(self.atgmCommand_data.start_command)

        # key press to start detection
        if event.char == 'd':
            self._imageProcessor.detect_run(self._first_detect)
            self._first_detect = False


    def _init_atgmConfigTab(self):

        # declare a holder frame
        self.atgmConfig_frame = ttk.LabelFrame(self.atgmconfigTab, text='Configure:', width=self.width, height=self.height)
        self.atgmConfig_frame.grid(row=0, column=0)


        # device combobox for retrieving ports
        self.atgmConfig_device_text = tk.StringVar()
        self.atgmConfig_device_combobox = ttk.Combobox(self.atgmConfig_frame, width=12, textvariable=self.device_text, state='readonly')
        self.atgmConfig_device_combobox['values'] = self.__populateDeviceCombobox__()
        self.atgmConfig_device_combobox.grid(row=1, column=0)
        self.atgmConfig_device_label = ttk.Label(self.atgmConfig_frame, text='Select port:')
        self.atgmConfig_device_label.grid(row=0, column=0)

        # declaration of world calibration button
        self.worldCalibButton = ttk.Button(self.atgmConfig_frame, text='Turret World Calibration', command = self._worldCalibrationhandler)
        self.worldCalibButton.grid(row=2, column=0)

        # declaration of scenario calibration button
        self.scenarioCalibButton = ttk.Button(self.atgmConfig_frame, text='Turret Scenario Calibration', command=self._scenarioCalibrationhandler)
        self.scenarioCalibButton.grid(row=3, column=0)

    # button event handler for world calibration
    def _worlCalibrationhandler(self):
        self._worldcalibrator = calibrator.ATGMCalibrator()
        self._worldcalibrator.start()

    # button event handler for scenario calibration
    def _scenarioCalibrationhandler(self):
        self._scenarioCalibThread = Thread(target=self._scenario_thread_handler, name='scenario calibration thread')
        self._scenarioCalibThread.start()

    # thread handler for world calibration thread
    def _world_thread_handler(self):
        pass

    # thread handler for scenario calibration thread
    def _scenario_thread_handler(self):
        pass


    def openport(self):
        """
        opens serial port
        """
        self._atgmMedia = AC.SerialMedia(unix_path_to_port=self.device_text.get(), baudrate=self.baudrate.get())
        if self._atgmMedia.is_open:
            self.echoScrolledTextBox.insert('[Connected]...\n')
            self._atgmMedia.responseEvent += self._responseRecieved
        else:
            self.echoScrolledTextBox.insert('[Port not found]...\n')
        return

    def send(self):
        """
        Takes in  commands in ascii/hex/
        """
        data_string = self.command.get()
        if self.hexradvar.get() == "hex":
            if self.hex_compute.check_for_hex(data_string):
                data_to_send = self.hex_compute.convert_hex_to_bytes(data_string)
            else:
                msg.showinfo('Value Error','The given command is not in the hex format: please prefix your command with a <0x>, sample command - 0x0123434f')
                return
        else:
            data_to_send = data_string.encode('utf-8')
        self._atgmMedia.send(data_send) #implement response tally
        return

    def openport_atgmCommand(self):
        if self._atgmMedia is not None:
            self._atgmMedia.release()
            self._atgmMedia = None
        self._atgmMedia = AC.SerialMedia(unix_path_to_port=self.atgmCommand_device_text.get(), baudrate=38400)
        self._atgmMedia.responseEvent += self._atgmCommandResponseRecieved
        self._atgmMedia.steps_responseEvent += self._atgm_stepsResponseRecieved
        if self._atgmMedia.is_open:
            self.atgmCommand_openPort_label.config(text="Active")

    def send_atgmCommand(self):
        # implement
        self._construct_atgmCommand()
        self._atgmMedia.send(self.atgmCommand_data.command)
        pass

    # function to construct the command from the user entered data
    def _construct_atgmCommand(self):
        # Azimuth motor direction
        if self.atgmCommand_azi_dir_text.get() == 'Right':
            self.atgmCommand_data.Azi_dir = 0
        else:
            self.atgmCommand_data.Azi_dir = 1
        # Azimuth motor resolution
        self.atgmCommand_data.Azi_res = self.atgmCommand_azi_res_text.get()
        # Azimuth RPM
        self.atgmCommand_data.Azi_RPM = int(self.atgmCommand_azi_RPM_text.get())
        # Azimuth steps
        self.atgmCommand_data.Azi_steps = int(self.atgmCommand_azi_steps_text.get())

        # Elevation motor direction
        if self.atgmCommand_ele_dir_text.get() == 'Up':
            self.atgmCommand_data.Ele_dir = 0
        else:
            self.atgmCommand_data.Ele_dir = 1

        # Elevation motor resolution
        self.atgmCommand_data.Ele_res = self.atgmCommand_ele_res_text.get()
        # Elevation RPM
        self.atgmCommand_data.Ele_RPM = int(self.atgmCommand_ele_RPM_text.get())
        # Elevation steps
        self.atgmCommand_data.Ele_steps = int(self.atgmCommand_ele_steps_text.get())


    def _atgmCommandResponseRecieved(self, data):
        #print("came out of atgmComms: OK packet")
        pass

    def _atgm_stepsResponseRecieved(self, data):
        #print("came out of atgm comms: steps packet")
        azi_dir = data[0]
        ele_dir = data[1]
        azi_steps = [data[2], data[3], data[4], data[5]]
        ele_steps = [data[6], data[7], data[8], data[9]]
        if azi_dir == 0:
            self._atgmState.Azimuth_steps += struct.unpack(">L", data[2:6])[0]
        else:
            self._atgmState.Azimuth_steps -= struct.unpack(">L", data[2:6])[0]
        if ele_dir == 0:
            self._atgmState.Elevation_steps += struct.unpack(">L", data[6:])[0]
        else:
            self._atgmState.Elevation_steps -= struct.unpack(">L", data[6:])[0]

        text = 'Elevation steps: '+ str(self._atgmState.Elevation_steps)
        #self.atgmCommand_elevation_steps_label.config(text=text)


    def _responseRecieved(self, data):
        """
        displays the data recieved onto the output echo box(echoScrolledTextBox)
        """
        self.echoScrolledTextBox.insert('\n'+data+'\n')




    def __populateDeviceCombobox__(self):

        if os.name == 'nt':
            return ('COM1', 'COM3')
        else:
            pattern = 'tty.'
            result = ()
            file_path = '/dev/'
            files = os.listdir(file_path)
            for file in files:
                if pattern in file:
                    file = file_path+file
                    result = result + (file,)
            return result


    def run(self):
        self.root.mainloop()
        return None

    def _exit(self):
        #pdb.set_trace()
        

        #self._imageProcessor.stop()
        #self._imageProcessor._videoThread.join()
        #self._imageProcessor.__del__()
        #time.sleep(2)

        #pdb.set_trace()
        #time.sleep(5)
        #print(threading.active_count())
        #print(threading.enumerate())
        #time.sleep(10)
        print("destroying window")
        self.root.destroy()
        return None

        #sys.exit()

    def _image_processor_clean_up(self):
        '''
        cleans up the image processor threading variables
        '''
        self._imageProcessor.DetectionEvent -= self._detection_event_handler
        self._imageProcessor.TrackEvent -= self._track_event_handler
        self._imageProcessor.frameEvent -= self._frame_event_handler
        self._imageProcessor.stop()
        if self._atgmMedia is not None:
            self._atgmMedia.release()
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

    def leftclick(self, event):
        """mouse leftclick event handler, selects the box to be tracked"""
        print("came here")
        if self._first_track:
            x = event.x
            y = event.y
            point = (x, y)
            roi_list = self.boxes
            for roi in roi_list:
                if self.point_in_box(point, roi):
                    self.tracking_roi = roi
            
            print("first_track")
            print("roi Initialized: ", self.tracking_roi)
            self._imageProcessor.track_run(self.tracking_roi,
                                           self.latest_frame,
                                           self._first_track, False)
            self._first_track = False
            return None

    # release all variables
    # def release(self):
    #     self._imageProcessor.stop()
        


def main():
    window = Atgm_Diagnostic_GUI()
    window.run()
    print(threading.active_count())
    print(threading.enumerate())
    print("quiting")
    #time.sleep(5)


if __name__ == "__main__":
    main()


