
'''
Click Button Logic:

"Fetch Available Routes:" -> self.fetch_routes_list_btn -> clicked=self.fetch_routes_list -> database/fetch_table_list.php
"Select route:" -> self.routeCombo -> self.selectRoute -> database/select_table.php
"Reverse the imported route:" -> clicked=self.clickMethod_flip_route -> self.draw_black_crosses(self.fetched_coordinates_list, line_colour)
"Add Route Snippet:" -> clicked=self.clickMethod_add_route -> database/des_coords.php -> tableName="des_coords" -> self.draw_black_crosses(self.main_coords_list, line_colour)
"Delete the last waypoint:" -> clicked=self.clickMethod_del_waypoint -> self.main_coords_list = self.main_coords_list[:-1] -> self.draw_black_crosses(self.main_coords_list, line_colour)
"Delete all waypoints:" -> clicked=self.clickMethod_del_all_waypoints -> self.draw_black_crosses(self.main_coords_list, line_colour)
"Clear Waypoints Not Yet Added to 'Main':" -> clicked=self.clear_waypoint_crosses -> self.draw_black_crosses(self.main_coords_list, line_colour)
"Delete selected table:" -> clicked=self.clickMethod_del_table -> database/delete_table.php
"New table for route:" -> clicked=self.clickMethod_create_route -> database/create_table.php -> self.clear_waypoint_crosses()
'Historical coords to download:' -> clicked.connect(self.clickMethod_fetch_hist_coords) -> self.parse_downloaded_data_string(ID_from_value,ID_to_value) -> database/show_data_simple_02.php -> self.draw_black_crosses(self.hist_coords_list, line_colour)
"ThrottleA", "ThrottleB" -> self.clickMethod_throttleSliders -> self.writeThrottleData(throttleASlider_value, throttleBSlider_value) -> database/control_01.php -> table = 'control'
'Database Readout:' -> self.box_weed_database_label / self.box_weed_database_line -> database/show_data_min.php 
self.weed_database_poller -> database_parsing(self) -> database/show_data_min.php -> eg. self.singlelineEdit_ID.setText(myString[0])  # ID -> hbox_layout_ID.addWidget(self.singlelineEdit_ID)
self.map_plot_poller -> self.update_plot -> self.map_canvas.draw()
"Send Main List to Control:" -> send_main_coords_post_list_btn -> clicked=self.send_main_coords_post_list -> control_room_database/send.php -> control_room table
'''
import passwords
import matplotlib.pyplot as plt
import matplotlib.text
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib import image
from matplotlib.offsetbox import (OffsetImage, AnnotationBbox)
from PyQt5.QtWidgets import QApplication, QWidget
import cartopy.crs as ccrs
import cartopy.io.img_tiles as cimgt
from pyqtgraph import PlotWidget, plot
import pyqtgraph as pg
import sys  # We need sys so that we can pass argv to QApplication
import os
from random import randint
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5 import QtCore, QtGui, QtWidgets, QtSerialPort
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtCore import QUrl, pyqtSlot, pyqtSignal, QObject
from PyQt5.QtWidgets import QPushButton, QMessageBox
from PyQt5.QtCore import pyqtSignal, QObject
from PyQt5.QtWidgets import (
    QApplication,
    QCheckBox,
    QFormLayout,
    QLineEdit,
    QTextEdit,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QComboBox,
    QApplication,
    QComboBox,
    QFormLayout,
    QLineEdit,
    QStackedLayout,
    QVBoxLayout,
    QWidget,
    QLabel,
    QPushButton,
)
from pyproj import CRS
from pyproj import Transformer
import urllib.request
import random
import scipy
import numpy as np
import time
import requests
import json
import re
from PyQt5 import QtCore

import warnings
warnings.filterwarnings("ignore")  # Suppress all Matplotlib warnings

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.window = Window(self)
        _widget = QWidget()
        _layout = QVBoxLayout(_widget)
        _layout.addWidget(self.window)
        self.setCentralWidget(_widget)
        # left, top, width, height.
        # self.setGeometry(800, 500, 1280, 720)
        # self.setGeometry(800, 500, 1280, 520)
        self.setGeometry(0, 0, 3000, 1750)
        # self.showFullScreen()

class Window(QWidget):
    def __init__(self, parent):
        super(Window, self).__init__(parent)
        self.setWindowTitle("WEEDINATOR")
        # self.__controls() # This is for waypointplanner.html
        self.plot_objects_a = []  # Create a list to store plot objects
        self.des_coords_list = [[None,None]]
        self.coords_list = [[None,None]]
        self.fetched_list_of_tables = {}
        self.main_coords_list = []
        self.fetched_coordinates_list = []
        self.hist_coords_list = [[None,None]]  # Historical coordinates from weedinator table
        self.len_fetched_coordinates_list = 0
        self.annotation_object_1 = None
        self.annotation_object_2 = None
        self.selected_route = None

        self.my_busy_flag_01 = False
        self.my_busy_flag_02 = False
        self.my_busy_flag_03 = False
        self.my_busy_flag_04 = False
        self.__myLayout()
        # self.__receiveSerial()
        # self.connectToSerialPort()
        
        # One off current data aquisition:
        self.database_parsing()
        
        # Create a QTimer object:
        self.weed_database_poller = QtCore.QTimer()
        self.weed_database_poller.setInterval(2000) # 20000
        self.weed_database_poller.timeout.connect(self.database_parsing)
        self.weed_database_poller.start()
        
        # Create a QTimer object:
        self.map_plot_poller = QtCore.QTimer()
        self.map_plot_poller.timeout.connect(self.update_plot)  # Connect timer to plot update
        self.map_plot_poller.start(2000)  # Refresh every 5 seconds (adjust as needed)
        
        # Create a QTimer object:
        self.map_plot_poller_fast = QtCore.QTimer()
        self.map_plot_poller_fast.timeout.connect(self.update_plot_fast)  # Connect timer to plot update
        self.map_plot_poller_fast.start(2000)  # Refresh every 2 seconds (adjust as needed)
        
        # Create a QTimer object:
        self.busy_poller = QtCore.QTimer()        
        self.busy_poller.timeout.connect(self.update_busy_status)  # Connect timer to update_busy_status
        self.busy_poller.start(50)
        
        
        self.setStyleSheet("background-color: black;")
        
    def update_busy_status(self):
        num_coords = len(self.des_coords_list)
        box_23_text = str(num_coords -1)
        self.singlelineEdit_num_waypoints.setText(box_23_text)
                
        if (self.my_busy_flag_01 == True) or (self.my_busy_flag_02 == True) or (self.my_busy_flag_03 == True) or (self.my_busy_flag_04 == True):
            box_24_text = "SYSTEM IS BUSY"
        else:
            box_24_text = "SYSTEM IS FREE"

        self.singlelineEdit_24.setText(box_24_text)

    def update_plot_fast(self):
        # Refresh map_canvas
        # print("Update plot !!")
        #TODO: why does the following line not update the canvas?:
        self.map_canvas.draw()
    
        
    def update_plot(self):
        self.my_busy_flag_01 = True
        '''
        self.path = '/home/rat/Documents/WEEDINATOR/tile_workshop.jpg'
        self.myImage = image.imread(self.path)
        self.imagebox = OffsetImage(self.myImage, zoom = 0.3210,  alpha=0.1)
        self.aa = AnnotationBbox(self.imagebox, (-472065.941097333, 7039185.849817743), frameon = False)
        self.ax.add_artist(self.aa)
        '''

        print("GPS coords: " + str(self.act_lat_float)  + " , " + str(self.act_lon_float))
        print("Heading: " + str(self.act_heading_float))
        
        crs_in = CRS.from_epsg("4326")  # webGPS
        crs_out = CRS.from_epsg("3857")   # Mercator
        transformerC = Transformer.from_crs(crs_in, crs_out)
        x = self.act_lat_float
        y = self.act_lon_float
        self.merc = transformerC.transform(x, y)
        print("merc: ", self.merc)

        '''
        self.image_file = "/home/rat/Documents/WEEDINATOR/small-tractor-transparent-background_03.png"
        self.robot = image.imread(self.image_file)
        self.imagebox = OffsetImage(self.robot, zoom = 0.23)
        '''
        
        global ab
        global ac
        # global ad

        # global robot_rotated
        # Clear the previous image annotation if it exists
        #  and (self.plot_objects_a is not None):
        try:
            self.ab.remove()
            self.ac.remove()
            # self.ad.remove()    # For some reason this fails.
            # print("operaton 1 succeeded !!")
        except:
            pass
            # print("operaton 1 failed !!")


        self.robot_rotated = scipy.ndimage.rotate(self.robot, (self.act_heading_float) * -1)
        imagebox = OffsetImage(self.robot_rotated, zoom = 0.15)
        self.ab = AnnotationBbox(imagebox, (self.merc[0],self.merc[1]), frameon = False)
        self.ax.add_artist(self.ab)
        
        rotated = scipy.ndimage.rotate(self.blue_arrow, (self.act_heading_float - self.act_steer_angle_float/10) * -1)
        imagebox = OffsetImage(rotated, zoom = 0.23)
        self.ac = AnnotationBbox(imagebox, ((self.merc[0]),(self.merc[1])), frameon = False)
        self.ax.add_artist(self.ac)
        
        # This following section draws black crosses and a blue line between them:
        #TODO: turn this into a function.
        self.path = '/home/rat/Documents/WEEDINATOR/black_cross.png'
        self.black_cross = image.imread(self.path)
        imagebox = OffsetImage(self.black_cross, zoom = 0.15)
        num_coords = len(self.des_coords_list)
        print("num_coords:", num_coords)
        # des_coords_list[i][0]
        
        # TODO: This will keep adding arrows over and over again to the same locations !!!
        # self.plot_objects_a = []  # Create a list to store plot objects
        self.plot_objects_b = []  # Create a list to store plot objects

        for i in range(1, num_coords - 1):
            x1= self.des_coords_list[i][0]
            y1 = self.des_coords_list[i][1]
            x2= self.des_coords_list[i+1][0]
            y2 = self.des_coords_list[i+1][1]
            if x1 != None:
                self.merc1 = transformerC.transform(x1, y1)
                self.merc2 = transformerC.transform(x2, y2)

                # Corrected code using ax.arrow()
                print("Example of arrow length: ")
                print("Arrow length: ",(self.merc2[0] - self.merc1[0]))
                line_colour = 'b'

                # Step 1: Draw the full line first.
                # This ensures a continuous line is visible.
                self.ae = self.ax.plot([self.merc1[0], self.merc2[0]], [self.merc1[1], self.merc2[1]], color=line_colour, linestyle='-', marker='')

                # Step 2: Define a fraction to control the arrowhead's position.
                # 0.5 is the midpoint. A smaller value moves it closer to self.merc1.
                # A larger value (up to 1.0) moves it closer to self.merc2.
                arrow_position_fraction = 0.75

                # Step 3: Calculate the new arrowhead position. This will be the new 'xy' parameter.
                arrowhead_x = self.merc1[0] + (self.merc2[0] - self.merc1[0]) * arrow_position_fraction
                arrowhead_y = self.merc1[1] + (self.merc2[1] - self.merc1[1]) * arrow_position_fraction

                # Step 4: Define a very short displacement for the arrow's tail.
                # This ensures the arrow shaft is drawn from just behind the head.
                # We're calculating a tiny step back (0.01 of the total line length).
                back_step_x = (self.merc2[0] - self.merc1[0]) * 0.01
                back_step_y = (self.merc2[1] - self.merc1[1]) * 0.01

                # Step 5: Use ax.annotate() with the new calculations.
                # The arrow head points to (arrowhead_x, arrowhead_y),
                # and the tail starts from a point just behind it.
                self.annotation_object_1 = self.ax.annotate('',
                                xy=(arrowhead_x, arrowhead_y),
                                xytext=(arrowhead_x - back_step_x, arrowhead_y - back_step_y),
                                arrowprops=dict(arrowstyle='->', lw=2, color=line_colour, mutation_scale=40))


                # Draw line using Matplotlib
                # self.ae = self.ax.plot([self.merc1[0], self.merc2[0]], [self.merc1[1], self.merc2[1]], color='b')  # Blue line by default
                # plt.plot([self.merc1[0], self.merc2[0]], [self.merc1[1], self.merc2[1]])
                
                self.ad = AnnotationBbox(imagebox, ((self.merc1[0]), (self.merc1[1])), frameon=False)
                self.ax.add_artist(self.ad)
                self.plot_objects_a.append(self.ad)  # Store the plot object
                self.plot_objects_b.append(self.ae)  # Store the plot object
                
        # Plot the last black cross:
        x1= self.des_coords_list[num_coords-1][0]
        if x1 != None:
            x1= self.des_coords_list[num_coords-1][0]
            y1 = self.des_coords_list[num_coords-1][1]
            self.merc1 = transformerC.transform(x1, y1)
            self.ad = AnnotationBbox(imagebox, ((self.merc1[0]), (self.merc1[1])), frameon=False)
            self.ax.add_artist(self.ad)
            self.plot_objects_a.append(self.ad)  # Store the plot object
        
        print("")
        # Refresh map_canvas
        self.map_canvas.draw()
        self.my_busy_flag_01 = False

    def draw_black_crosses(self,coords_list,line_colour):
        '''
        'b' for blue
        'g' for green
        'r' for red
        'c' for cyan
        'm' for magenta
        'y' for yellow
        'k' for black
        'w' for white
        '''
        crs_in = CRS.from_epsg("4326")  # webGPS
        crs_out = CRS.from_epsg("3857")   # Mercator
        transformerC = Transformer.from_crs(crs_in, crs_out)

        self.path = '/home/rat/Documents/WEEDINATOR/black_cross.png'
        self.black_cross = image.imread(self.path)
        imagebox = OffsetImage(self.black_cross, zoom = 0.15)
        print(f"\nTotal coordinate pairs: {len(coords_list)}")
        num_coords = len(coords_list)
        print("num_coords:",num_coords)
        
        # TODO: This will keep adding arrows over and over again to the same locations ?
        # self.plot_objects_a = []  # Create a list to store plot objects
        self.plot_objects_b = []  # Create a list to store plot objects

        # Remove the annotation object created in 'update_plot' function:
        # self.annotation_object_1.remove() # Already done in function call
        # for i in range(1, num_coords - 1):
        for i in range(0, num_coords):
            x1= coords_list[i][0]
            y1 = coords_list[i][1]
            try:
                x2= coords_list[i+1][0]  # Might be out of range.
                y2 = coords_list[i+1][1]  # Might be out of range.
            except:
                pass
            if x1 != None:
                self.merc1 = transformerC.transform(x1, y1)
                self.merc2 = transformerC.transform(x2, y2)

                # Step 1: Draw the full line first.
                # This ensures a continuous line is visible.
                self.ae = self.ax.plot([self.merc1[0], self.merc2[0]], [self.merc1[1], self.merc2[1]], color=line_colour, linestyle='-', marker='')

                # Step 2: Define a fraction to control the arrowhead's position.
                # 0.5 is the midpoint. A smaller value moves it closer to self.merc1.
                # A larger value (up to 1.0) moves it closer to self.merc2.
                arrow_position_fraction = 0.75

                # Step 3: Calculate the new arrowhead position. This will be the new 'xy' parameter.
                arrowhead_x = self.merc1[0] + (self.merc2[0] - self.merc1[0]) * arrow_position_fraction
                arrowhead_y = self.merc1[1] + (self.merc2[1] - self.merc1[1]) * arrow_position_fraction

                # Step 4: Define a very short displacement for the arrow's tail.
                # This ensures the arrow shaft is drawn from just behind the head.
                # We're calculating a tiny step back (0.01 of the total line length).
                back_step_x = (self.merc2[0] - self.merc1[0]) * 0.01
                back_step_y = (self.merc2[1] - self.merc1[1]) * 0.01

                # Step 5: Use ax.annotate() with the new calculations.
                # The arrow head points to (arrowhead_x, arrowhead_y),
                # and the tail starts from a point just behind it.
                self.annotation_object_2 = self.ax.annotate('',
                                xy=(arrowhead_x, arrowhead_y),
                                xytext=(arrowhead_x - back_step_x, arrowhead_y - back_step_y),
                                arrowprops=dict(arrowstyle='->', lw=2, color=line_colour, mutation_scale=40))

                # Draw line using Matplotlib
                # self.ae = self.ax.plot([self.merc1[0], self.merc2[0]], [self.merc1[1], self.merc2[1]], color=line_colour)
                
                self.ad = AnnotationBbox(imagebox, ((self.merc1[0]), (self.merc1[1])), frameon=False)
                self.ax.add_artist(self.ad)
                self.plot_objects_a.append(self.ad)  # Store the plot object
                self.plot_objects_b.append(self.ae)  # Store the plot object
                
        # Plot the last black cross:
        # x1= self.coords_list[num_coords-1][0]

        try:
            if x1 != None:
                x1= coords_list[num_coords-1][0]
                y1 = coords_list[num_coords-1][1]
                self.merc1 = transformerC.transform(x1, y1)
                self.ad = AnnotationBbox(imagebox, ((self.merc1[0]), (self.merc1[1])), frameon=False)
                self.ax.add_artist(self.ad)
                self.plot_objects_a.append(self.ad)  # Store the plot object
        except:
            pass

        # Refresh map_canvas
        self.map_canvas.draw()
        self.my_busy_flag_01 = False
        
    def __myLayout(self):
        theme = "light"
        
        if theme == "light":

            styleSheet_page_1_01 = "font: 11pt; border: 2px solid black; border-radius: 5px; background-color: #ffffff;"
            styleSheet_page_2_01 = "font: 11pt; border: 2px solid black; border-radius: 5px; background-color: #ffffff;"
            # styleSheet_page_3_00 = "font: 25pt; font: bold; border: 2px solid black; border-radius: 10px; background-color: #ffffff;"
            # styleSheet_page_3_01 = "font: 25pt; font: bold; border: 5px solid black; border-radius: 10px; background-color: #edfdfe;"
            # styleSheet_page_3_02 = "font: 25pt; font: bold; border: 5px solid black; border-radius: 10px; background-color: #edfef0;"
            styleSheet_page_3_00 = "font: 20pt; border: 2px solid black; border-radius: 5px; background-color: #ffffff;"
            styleSheet_page_3_01 = "font: 20pt; border: 2px solid black; border-radius: 5px; background-color: #ffffff;"
            styleSheet_page_3_02 = "font: 20pt; border: 2px solid black; border-radius: 5px; background-color: #ffffff;"
            styleSheet_page_3_03 = "font: 20pt; border: 2px solid black; border-radius: 5px; background-color: #ffffff;"

            styleSheet_top_banner_combo_btn = """
                QComboBox {
                    color: black;
                    font: 20pt;
                    border: 2px solid black;
                    border-radius: 5px;
                    background-color: #ffffff;
                }
                QComboBox::hover {
                    background-color: lightgreen;
                }
            """
            
            styleSheet_top_banner_click_btn = """
                QPushButton {
                    font: 20pt;
                    border: 2px solid black;
                    border-radius: 5px;
                    color: black;
                    background-color: #b8eefc;
                }
                QPushButton::hover {
                    background-color: lightgreen;
                }
            """
            
        stylesheet = """

        """
            
            
        if theme == "dark":

            styleSheet_page_1_01 = "font: 5pt; border: 2px solid black; border-radius: 5px; background-color: #000000;"
            styleSheet_page_2_01 = "font: 11pt; border: 2px solid black; border-radius: 5px; background-color: #000000;"
            # styleSheet_page_3_00 = "font: 25pt; font: bold; border: 2px solid black; border-radius: 10px; background-color: #ffffff;"
            # styleSheet_page_3_01 = "font: 25pt; font: bold; border: 5px solid black; border-radius: 10px; background-color: #edfdfe;"
            # styleSheet_page_3_02 = "font: 25pt; font: bold; border: 5px solid black; border-radius: 10px; background-color: #edfef0;"
            styleSheet_page_3_00 = "font: 20pt; color: yellow; border: 2px solid yellow; border-radius: 5px; background-color: #000000;"
            styleSheet_page_3_01 = "font: 20pt; color: yellow; border: 2px solid yellow; border-radius: 5px; background-color: #000000;"
            styleSheet_page_3_02 = "font: 20pt; color: yellow; border: 2px solid yellow; border-radius: 5px; background-color: #000000;"
            styleSheet_page_3_03 = "font: 20pt; color: yellow; border: 2px solid yellow; border-radius: 5px; background-color: #000000;"
            styleSheet_top_banner_combo_btn ="QComboBox ""{""color: yellow;; font: 20pt; color: yellow; border: 2px solid black; border-radius: 5px; background-color: #000000;""} QComboBox::hover""{""background-color : lightgreen;""}"
            styleSheet_top_banner_click_btn ="QPushButton ""{""font: 20pt; color: yellow; border: 2px solid yellow;; border-radius: 5px; background-color: #000000;""} QPushButton::hover""{""background-color : lightgreen;""}"

        # Cartopy tile request
        self.request = cimgt.QuadtreeTiles()
        
        # Create the figure and axes within a map canvas
        self.fig, self.ax = plt.subplots(figsize=(32, 24), subplot_kw=dict(projection=self.request.crs))
        self.fig.tight_layout()
        
        # Define extent
        # Beehive Orchard:
        # 53.30314228904184, -4.242659416926793
        # 53.30406388350089, -4.242715054143694
        # 53.30407379928249, -4.240838030141921
        # 53.303148121980676, -4.240826317043625
        
        crs_in = CRS.from_epsg("4326")  # webGPS
        crs_out = CRS.from_epsg("3857")   # Mercator
        transformerC = Transformer.from_crs(crs_in, crs_out)
        
        extent_behive_orchard = [-4.242715054143694, -4.240426317043625, 53.30314228904184, 53.30407379928249]
        behive_orchard_centre = [(extent_behive_orchard[0] + extent_behive_orchard[1])/2 , (extent_behive_orchard[2] + extent_behive_orchard[3])/2]
        behive_orchard_centre_merc = transformerC.transform(behive_orchard_centre[1], behive_orchard_centre[0])

        extent_workshop = [-4.241520, -4.239761, 53.302347, 53.303044]
        workshop_center = [-472065.941097333, 7039185.849817743]
        workshop_tile_zoom = 0.3210
        behive_orchard_zoom = 0.466

        # Set extent and add base map image to axes
        self.ax.set_extent(extent_workshop)
        self.ax.add_image(self.request, 20)
        
        #self.path = '/home/rat/Documents/WEEDINATOR/tiles/beehive_orchard_tile.jpg'
        self.path = '/home/rat/Documents/WEEDINATOR/tiles/tile_workshop.jpg'
        self.myImage = image.imread(self.path)
        self.imagebox = OffsetImage(self.myImage, zoom = workshop_tile_zoom,  alpha=0.5)
        self.aa = AnnotationBbox(self.imagebox, (workshop_center), frameon = False)
        self.ax.add_artist(self.aa)

        self.image_file = "/home/rat/Documents/WEEDINATOR/small-tractor-transparent-background_02.png"
        self.robot = image.imread(self.image_file)
        self.robot = (self.robot * 255).astype(np.uint8)

        # self.image_file = "/home/rat/Documents/WEEDINATOR/tractor_wheel_LHS.png"
        # self.wheel_image = image.imread(self.image_file)
        # self.wheel_image = (self.wheel_image * 255).astype(np.uint8)

        self.image_file = "/home/rat/Documents/WEEDINATOR/blue_arrow.png"
        self.blue_arrow = image.imread(self.image_file)
        self.blue_arrow = (self.blue_arrow * 255).astype(np.uint8)

        # Create the map canvas:
        self.map_canvas = FigureCanvas(self.fig)
        # Add mouse click event:
        self.map_canvas.mpl_connect('button_press_event', self.on_map_click)  # Connect click event

        # Create the stacked layout for enabling page changes:
        stackedLayout = QStackedLayout()
        
        # Create the first page:
        page1 = QWidget()
        page1.setStyleSheet(styleSheet_page_3_00)

        # Create an outer layout for page 1, hierarchy 0:
        # self.outerLayout_page1 = QHBoxLayout()

        # Create the main layout panels:

        topLevelLayout = QVBoxLayout()
        topBannerLayout = QHBoxLayout()
        topBanner = QWidget()
        topBanner.setStyleSheet(styleSheet_page_3_00)
        topBanner.setLayout(topBannerLayout)
        topLevelLayout.addWidget(topBanner)

        topLevelLayout.addLayout(stackedLayout)
        # topBannerLayout.addLayout(stackedLayout)
        outerLayout = QHBoxLayout()
        
        # Add outerLayout to page 1:
        page1.setLayout(outerLayout)
        stackedLayout.addWidget(page1)

        sideBannerLayout = QVBoxLayout()
        outerLayout.addLayout(sideBannerLayout)       
        
        mapBox= QVBoxLayout()          
        outerLayout.addLayout(mapBox)
        
        row_1 = QHBoxLayout()
        sideBannerLayout.addLayout(row_1)
        row_2 = QHBoxLayout()
        sideBannerLayout.addLayout(row_2)
        row_3 = QHBoxLayout()
        sideBannerLayout.addLayout(row_3)
        row_4 = QHBoxLayout()
        sideBannerLayout.addLayout(row_4)      
        
        # Populate the panels:
        # Populate top banner:
        # self.connect_btn = QtWidgets.QPushButton("Connect", clicked=self.connectToSerialPort)
        # self.connect_btn.setStyleSheet(styleSheet_top_banner_click_btn)
        # self.connect_btn.setFixedWidth(300)

        # Create a horizontal layout
        h_layout = QtWidgets.QHBoxLayout()

        self.box_weed_database_label = QLabel(self)
        self.box_weed_database_label.setStyleSheet(styleSheet_page_3_03)
        self.box_weed_database_label.setText('Database Readout:')
        self.box_weed_database_label.setFixedWidth(280)

        self.box_weed_database_line = QtWidgets.QLineEdit(readOnly=True)
        self.box_weed_database_line.setStyleSheet(styleSheet_page_3_03)

        # Add the widgets to the layout
        # h_layout.addWidget(self.box_weed_database_label)
        # h_layout.addWidget(self.box_weed_database_line)
        
        # Create and connect the combo box to switch between pages
        self.pageCombo = QComboBox()
        self.pageCombo.setFixedWidth(150)
        self.pageCombo.setStyleSheet(styleSheet_top_banner_combo_btn)
        self.pageCombo.addItems(["Page 1", "Page 2", "Page 3"])
        self.pageCombo.activated.connect(self.switchPage)
        
        quit_button = QPushButton('Quit', self)
        quit_button.setFixedWidth(150)
        quit_button.setStyleSheet(styleSheet_top_banner_click_btn)
        quit_button.clicked.connect(QApplication.instance().quit)
        
        # Create a QLineEdit for displaying mouse click results
        self.mouse_click_data = QLineEdit()
        self.mouse_click_data.setReadOnly(True)  # Make it read-only
        self.mouse_click_data.setStyleSheet(styleSheet_page_3_03)
        self.mouse_click_data.setFixedWidth(600)
        
        # Add widgets to top banner:
        # h_layout.addWidget(self.connect_btn)
        h_layout.addWidget(self.box_weed_database_label)
        h_layout.addWidget(self.box_weed_database_line)
        h_layout.addWidget(self.pageCombo)
        h_layout.addWidget(self.mouse_click_data)
        h_layout.addWidget(quit_button)
        
        topBannerLayout.addLayout(h_layout)

        # Populate mapBox:
        self.map_canvas.setMinimumSize(QSize(2460, 1630))
        self.map_canvas.setMaximumSize(QSize(2460, 1630))
        mapBox.addWidget(self.map_canvas)
        
        # Populate sideBanner:
        # Create form layouts:
        #####################################################################
        # Data entry boxes, row_1:
        
        page1Form_1a = QFormLayout()
        page1Form_1a.setVerticalSpacing(5)
        page1Form_1b = QFormLayout()
        page1Form_1b.setVerticalSpacing(5)   
        page1Form_1c = QFormLayout()
        page1Form_1c.setVerticalSpacing(5)
        page1Form_1d = QFormLayout()
        page1Form_1d.setVerticalSpacing(5) 
        
        #####################################################################
        # Component details for sub row 1_1:
        page1Label_1a_1 = QLabel(self)
        page1Label_1a_1.setStyleSheet(styleSheet_page_3_01)
        page1Label_1a_1.setText('Waypoints to WEEDINATOR:')

        self.page1Line_1b_1 = QLineEdit(self)
        self.page1Line_1b_1.setStyleSheet(styleSheet_page_3_01)

        self.page1Button_1c_1 = QLineEdit(self)
        self.page1Button_1c_1.setStyleSheet(styleSheet_page_3_01)
        
        page1Button_1d_1 = QPushButton('SEND', self)
        page1Button_1d_1.setStyleSheet(styleSheet_top_banner_click_btn)
        page1Button_1d_1.clicked.connect(self.clickMethod_1a)

        page1Form_1a.addWidget(page1Label_1a_1)
        page1Form_1b.addWidget(self.page1Line_1b_1)
        page1Form_1c.addWidget(self.page1Button_1c_1)
        page1Form_1d.addWidget(page1Button_1d_1)
        
        #####################################################################
        # Component details for sub row 1_2:
        page1Label_1a_2 = QLabel(self)
        page1Label_1a_2.setStyleSheet(styleSheet_page_3_02)
        page1Label_1a_2.setText('Historical coords to download:')
        
        self.page1Line_1b_2 = QLineEdit(self)
        self.page1Line_1b_2.setStyleSheet(styleSheet_page_3_02)

        self.page1Line_1c_2 = QLineEdit(self)
        self.page1Line_1c_2.setStyleSheet(styleSheet_page_3_02)
        
        page1Button_1d_2 = QPushButton('SEND', self)
        page1Button_1d_2.setStyleSheet(styleSheet_top_banner_click_btn)
        page1Button_1d_2.clicked.connect(self.clickMethod_fetch_hist_coords)

        page1Form_1a.addWidget(page1Label_1a_2)
        page1Form_1b.addWidget(self.page1Line_1b_2)
        page1Form_1c.addWidget(self.page1Line_1c_2)
        page1Form_1d.addWidget(page1Button_1d_2)
        
        #####################################################################
        # Now add the two sub rows to the main row, row_1:
        row_1.addLayout(page1Form_1a)
        row_1.addLayout(page1Form_1b)
        row_1.addLayout(page1Form_1c)
        row_1.addLayout(page1Form_1d)
        
        #######################################################
        # Sliders, row_2:

        self.throttleASlider = QtWidgets.QSlider()
        self.throttleASlider.setStyleSheet(styleSheet_page_3_01)
        self.throttleASlider.setMinimumHeight(80)
        self.throttleASlider.setGeometry(QtCore.QRect(200, 200, 300, 50))
        self.throttleASlider.setOrientation(QtCore.Qt.Horizontal)
        
        # Set the minimum and maximum values for the slider's range
        self.throttleASlider.setMinimum(-50)
        self.throttleASlider.setMaximum(50)
        
        # Set the default position of the slider to 0
        self.throttleASlider.setValue(0)
  
        self.page1Label_2a = QtWidgets.QLabel()
        self.page1Label_2a.setAlignment(QtCore.Qt.AlignCenter)
        self.page1Label_2a.setStyleSheet(styleSheet_page_3_01)
        self.page1Label_2a.setGeometry(QtCore.QRect(230, 150, 301, 161)) 
          
        # set initial font size of label. 
        self.font = QtGui.QFont() 
        self.font.setPointSize(7) 
        self.page1Label_2a.setFont(self.font)
        self.page1Label_2a.setText("ThrottleA")
        # getting value changed signal 
        self.throttleASlider.valueChanged.connect(lambda: self.page1Label_2a.setText("ThrottleA = " + str(self.throttleASlider.value())))
        
        # page1Button_2a = QPushButton('SEND', self)
        # page1Button_2a.setStyleSheet(styleSheet_page_3_01)
        # page1Button_2a.clicked.connect(self.clickMethod_throttleSliders)
        
        page1Form_2a = QFormLayout()
        page1Form_2a.setVerticalSpacing(5)
        page1Form_2a.addWidget(self.throttleASlider)
        page1Form_2a.addWidget(self.page1Label_2a)
        # page1Form_2a.addWidget(page1Button_2a) # Not required
        
        # page1Form_2a = QFormLayout()
        # page1Form_2a.setVerticalSpacing(5)
        row_2.addLayout(page1Form_2a)
        
        ############################################################
        
        # Sliders, row_3:

        self.throttleBSlider = QtWidgets.QSlider()
        self.throttleBSlider.setStyleSheet(styleSheet_page_3_01)
        self.throttleBSlider.setMinimumHeight(80)
        self.throttleBSlider.setGeometry(QtCore.QRect(200, 200, 300, 50))
        self.throttleBSlider.setOrientation(QtCore.Qt.Horizontal)
  
        self.page1Label_3a = QtWidgets.QLabel()
        self.page1Label_3a.setAlignment(QtCore.Qt.AlignCenter)
        self.page1Label_3a.setStyleSheet(styleSheet_page_3_01)
        self.page1Label_3a.setGeometry(QtCore.QRect(230, 150, 301, 161)) 
          
        # set initial font size of label. 
        self.font = QtGui.QFont() 
        self.font.setPointSize(7) 
        self.page1Label_3a.setFont(self.font)
        self.page1Label_3a.setText("ThrottleB")
        # getting value changed signal 
        self.throttleBSlider.valueChanged.connect(lambda: self.page1Label_3a.setText("ThrottleB = " + str(self.throttleBSlider.value())))
        
        page1Button_3a = QPushButton('SEND', self)
        page1Button_3a.setStyleSheet(styleSheet_page_3_01)
        page1Button_3a.clicked.connect(self.clickMethod_throttleSliders)
        page1Button_3a.setStyleSheet(styleSheet_top_banner_click_btn)
        
        page1Form_3a = QFormLayout()
        page1Form_3a.setVerticalSpacing(5)
        page1Form_3a.addWidget(self.throttleBSlider)
        page1Form_3a.addWidget(self.page1Label_3a)
        page1Form_3a.addWidget(page1Button_3a)

        row_3.addLayout(page1Form_3a)
        
        ############################################################
        # Push button connections to associated functions:
        self.clear_waypoint_crosses_btn = QtWidgets.QPushButton("Clear", clicked=self.clear_waypoint_crosses)
        self.clear_waypoint_crosses_btn.setStyleSheet(styleSheet_top_banner_click_btn)
        self.clear_waypoint_crosses_btn.setFixedWidth(150)
        
        # Create a horizontal layout for the button and line edit
        hbox_layout_clear_waypoint_crosses = QHBoxLayout()
        hbox_layout_clear_waypoint_crosses.addSpacing(5)
        line_edit_clear_waypoint_crosses_1 = QLineEdit()
        line_edit_clear_waypoint_crosses_1.setText("Clear Waypoints Not Yet Added to 'Main':")
        hbox_layout_clear_waypoint_crosses.addWidget(line_edit_clear_waypoint_crosses_1)
        hbox_layout_clear_waypoint_crosses.addSpacing(5)
        hbox_layout_clear_waypoint_crosses.addWidget(self.clear_waypoint_crosses_btn)

        self.reset_database_btn = QtWidgets.QPushButton("Reset", clicked=self.reset_database)
        self.reset_database_btn.setStyleSheet(styleSheet_top_banner_click_btn)
        self.reset_database_btn.setFixedWidth(150)
        
        # Create a horizontal layout for the button and line edit
        hbox_layout_reset_database = QHBoxLayout()
        hbox_layout_reset_database.addSpacing(5)
        line_edit_reset_database_1 = QLineEdit()
        line_edit_reset_database_1.setText("Reset Database:")
        hbox_layout_reset_database.addWidget(line_edit_reset_database_1)
        hbox_layout_reset_database.addSpacing(5)
        hbox_layout_reset_database.addWidget(self.reset_database_btn)
        
        self.send_main_coords_post_list_btn = QtWidgets.QPushButton("Send", clicked=self.send_main_coords_post_list)
        self.send_main_coords_post_list_btn.setStyleSheet(styleSheet_top_banner_click_btn)
        self.send_main_coords_post_list_btn.setFixedWidth(150)
        
        # Create a horizontal layout for the 'Send Clicked Waypoints' button and line edit
        hbox_layout_main_coords_post = QHBoxLayout()
        hbox_layout_main_coords_post.addSpacing(5)
        line_edit_main_coords_post_1 = QLineEdit()
        line_edit_main_coords_post_1.setText("Send Main List to Control:")
        hbox_layout_main_coords_post.addWidget(line_edit_main_coords_post_1)
        hbox_layout_main_coords_post.addSpacing(5)
        hbox_layout_main_coords_post.addWidget(self.send_main_coords_post_list_btn)
        
        self.fetch_routes_list_btn = QtWidgets.QPushButton("Fetch", clicked=self.fetch_routes_list)
        self.fetch_routes_list_btn.setStyleSheet(styleSheet_top_banner_click_btn)
        self.fetch_routes_list_btn.setFixedWidth(150)
        
        # Create a horizontal layout for the 'Fetch Available Routes' button and line edit
        hbox_layout_refresh_routes_list = QHBoxLayout()
        hbox_layout_refresh_routes_list.addSpacing(5)
        line_edit_refresh_routes_list = QLineEdit()
        line_edit_refresh_routes_list.setText("Fetch Available Routes:")
        hbox_layout_refresh_routes_list.addWidget(line_edit_refresh_routes_list)
        hbox_layout_refresh_routes_list.addSpacing(5)
        hbox_layout_refresh_routes_list.addWidget(self.fetch_routes_list_btn)

        # Create a horizontal layout for the button and line edit
        hbox_layout_new_route = QHBoxLayout()
        hbox_layout_new_route.addSpacing(5)
        button_new_route = QPushButton("Create", clicked=self.clickMethod_create_route)
        # clickMethod_create_route()
        button_new_route.setStyleSheet(styleSheet_top_banner_click_btn)
        button_new_route.setFixedWidth(150)
        line_edit_new_route_1 = QLineEdit()
        line_edit_new_route_1.setText("New table for route:")
        self.line_edit_new_route_2 = QtWidgets.QLineEdit()
        hbox_layout_new_route.addWidget(line_edit_new_route_1)
        hbox_layout_new_route.addSpacing(5)
        hbox_layout_new_route.addWidget(self.line_edit_new_route_2)
        hbox_layout_new_route.addSpacing(5)
        hbox_layout_new_route.addWidget(button_new_route)
        
        # Create a horizontal layout for the Add Route Snippet button and line edit
        hbox_layout_add_route = QHBoxLayout()
        hbox_layout_add_route.addSpacing(5)
        button_add_route = QPushButton("Add", clicked=self.clickMethod_add_route)
        button_add_route.setStyleSheet(styleSheet_top_banner_click_btn)
        button_add_route.setFixedWidth(150)
        line_edit_add_route = QLineEdit()
        line_edit_add_route.setText("Add Route Snippet:")
        self.line_edit_add_route = QtWidgets.QLineEdit()
        hbox_layout_add_route.addWidget(line_edit_add_route)
        hbox_layout_add_route.addSpacing(5)
        hbox_layout_add_route.addWidget(button_add_route)
        
        # Create a horizontal layout for the flip route button and line edit
        hbox_layout_flip_route = QHBoxLayout()
        hbox_layout_flip_route.addSpacing(5)
        button_flip_route = QPushButton("Flip", clicked=self.clickMethod_flip_route)
        button_flip_route.setStyleSheet(styleSheet_top_banner_click_btn)
        button_flip_route.setFixedWidth(150)
        line_edit_flip_route = QLineEdit()
        line_edit_flip_route.setText("Reverse the imported route:")
        self.line_edit_flip_route = QtWidgets.QLineEdit()
        hbox_layout_flip_route.addWidget(line_edit_flip_route)
        hbox_layout_flip_route.addSpacing(5)
        hbox_layout_flip_route.addWidget(button_flip_route)
        
        # Create a horizontal layout for the delete single waypoint button and line edit
        hbox_layout_del_waypoint = QHBoxLayout()
        hbox_layout_del_waypoint.addSpacing(5)
        button_del_waypoint = QPushButton("Delete", clicked=self.clickMethod_del_waypoint)
        button_del_waypoint.setStyleSheet(styleSheet_top_banner_click_btn)
        button_del_waypoint.setFixedWidth(150)
        line_edit_del_waypoint = QLineEdit()
        line_edit_del_waypoint.setText("Delete the last waypoint:")
        self.line_edit_del_waypoint = QtWidgets.QLineEdit()
        hbox_layout_del_waypoint.addWidget(line_edit_del_waypoint)
        hbox_layout_del_waypoint.addSpacing(5)
        hbox_layout_del_waypoint.addWidget(button_del_waypoint)
        
        # Create a horizontal layout for the delete all waypoints button and line edit
        hbox_layout_del_all_waypoints = QHBoxLayout()
        hbox_layout_del_all_waypoints.addSpacing(5)
        button_del_all_waypoints = QPushButton("Delete", clicked=self.clickMethod_del_all_waypoints)
        button_del_all_waypoints.setStyleSheet(styleSheet_top_banner_click_btn)
        button_del_all_waypoints.setFixedWidth(150)
        line_edit_del_all_waypoints = QLineEdit()
        line_edit_del_all_waypoints.setText("Delete all waypoints:")
        self.line_edit_del_all_waypoints = QtWidgets.QLineEdit()
        hbox_layout_del_all_waypoints.addWidget(line_edit_del_all_waypoints)
        hbox_layout_del_all_waypoints.addSpacing(5)
        hbox_layout_del_all_waypoints.addWidget(button_del_all_waypoints)
        
        # Create a horizontal layout for the delete selected table button and line edit
        hbox_layout_del_table = QHBoxLayout()
        hbox_layout_del_table.addSpacing(5)
        button_del_table = QPushButton("Delete", clicked=self.clickMethod_del_table)
        button_del_table.setStyleSheet(styleSheet_top_banner_click_btn)
        button_del_table.setFixedWidth(150)
        line_edit_del_table = QLineEdit()
        line_edit_del_table.setText("Delete selected table:")
        self.line_edit_del_table = QtWidgets.QLineEdit()
        hbox_layout_del_table.addWidget(line_edit_del_table)
        hbox_layout_del_table.addSpacing(5)
        hbox_layout_del_table.addWidget(button_del_table)
        
        # Create a horizontal layout for the button and line edit
        hbox_layout_test = QHBoxLayout()
        hbox_layout_test.addSpacing(5)
        line_edit_test_1 = QLineEdit()
        line_edit_test_1.setText("Test")
        line_edit_test_1.setFixedWidth(300)
        line_edit_test_2 = QLineEdit()
        hbox_layout_test.addWidget(line_edit_test_1)
        hbox_layout_test.addSpacing(5)
        hbox_layout_test.addWidget(line_edit_test_2)
        
        # Create a horizontal layout for the button and line edit
        self.singlelineEdit_ID = QtWidgets.QLineEdit(readOnly=True)
        hbox_layout_ID = QHBoxLayout()
        hbox_layout_ID.addSpacing(5)
        line_edit_ID_1 = QLineEdit()
        line_edit_ID_1.setText("ID:")
        line_edit_ID_1.setFixedWidth(300)
        line_edit_ID_2 = QLineEdit()
        hbox_layout_ID.addWidget(line_edit_ID_1)
        hbox_layout_ID.addSpacing(5)
        hbox_layout_ID.addWidget(self.singlelineEdit_ID)
        
        # Create a horizontal layout for the button and line edit
        self.singlelineEdit_TIME = QtWidgets.QLineEdit(readOnly=True)
        hbox_layout_TIME = QHBoxLayout()
        hbox_layout_TIME.addSpacing(5)
        line_edit_TIME_1 = QLineEdit()
        line_edit_TIME_1.setText("TIME:")
        line_edit_TIME_1.setFixedWidth(300)
        line_edit_TIME_2 = QLineEdit()
        hbox_layout_TIME.addWidget(line_edit_TIME_1)
        hbox_layout_TIME.addSpacing(5)
        hbox_layout_TIME.addWidget(self.singlelineEdit_TIME)
        
        # Create a horizontal layout for the button and line edit
        self.singlelineEdit_act_lat = QtWidgets.QLineEdit(readOnly=True)
        hbox_layout_act_lat = QHBoxLayout()
        hbox_layout_act_lat.addSpacing(5)
        line_edit_act_lat_1 = QLineEdit()
        line_edit_act_lat_1.setText("act lat:")
        line_edit_act_lat_1.setFixedWidth(300)
        line_edit_act_lat_2 = QLineEdit()
        hbox_layout_act_lat.addWidget(line_edit_act_lat_1)
        hbox_layout_act_lat.addSpacing(5)
        hbox_layout_act_lat.addWidget(self.singlelineEdit_act_lat)
        
        # Create a horizontal layout for the button and line edit
        self.singlelineEdit_act_lon = QtWidgets.QLineEdit(readOnly=True)
        hbox_layout_act_lon = QHBoxLayout()
        hbox_layout_act_lon.addSpacing(5)
        line_edit_act_lon_1 = QLineEdit()
        line_edit_act_lon_1.setText("act lon:")
        line_edit_act_lon_1.setFixedWidth(300)
        line_edit_act_lon_2 = QLineEdit()
        hbox_layout_act_lon.addWidget(line_edit_act_lon_1)
        hbox_layout_act_lon.addSpacing(5)
        hbox_layout_act_lon.addWidget(self.singlelineEdit_act_lon)
        
        # Create a horizontal layout for the button and line edit
        self.singlelineEdit_act_heading = QtWidgets.QLineEdit(readOnly=True)
        hbox_layout_act_heading = QHBoxLayout()
        hbox_layout_act_heading.addSpacing(5)
        line_edit_act_heading_1 = QLineEdit()
        line_edit_act_heading_1.setText("act heading:")
        line_edit_act_heading_1.setFixedWidth(300)
        line_edit_act_heading_2 = QLineEdit()
        hbox_layout_act_heading.addWidget(line_edit_act_heading_1)
        hbox_layout_act_heading.addSpacing(5)
        hbox_layout_act_heading.addWidget(self.singlelineEdit_act_heading)
        
        # Create a horizontal layout for the button and line edit
        self.singlelineEdit_act_steer_angle = QtWidgets.QLineEdit(readOnly=True)
        hbox_layout_act_steer_angle = QHBoxLayout()
        hbox_layout_act_steer_angle.addSpacing(5)
        line_edit_act_steer_angle_1 = QLineEdit()
        line_edit_act_steer_angle_1.setText("act steer angle:")
        line_edit_act_steer_angle_1.setFixedWidth(300)
        line_edit_act_steer_angle_2 = QLineEdit()
        hbox_layout_act_steer_angle.addWidget(line_edit_act_steer_angle_1)
        hbox_layout_act_steer_angle.addSpacing(5)
        hbox_layout_act_steer_angle.addWidget(self.singlelineEdit_act_steer_angle)

        # Create a horizontal layout for the button and line edit
        self.singlelineEdit_act_throtA_val = QtWidgets.QLineEdit(readOnly=True)
        hbox_layout_act_throtA_val = QHBoxLayout()
        hbox_layout_act_throtA_val.addSpacing(5)
        line_edit_act_throtA_val_1 = QLineEdit()
        line_edit_act_throtA_val_1.setText("act throtA value:")
        line_edit_act_throtA_val_1.setFixedWidth(300)
        line_edit_act_throtA_val_2 = QLineEdit()
        hbox_layout_act_throtA_val.addWidget(line_edit_act_throtA_val_1)
        hbox_layout_act_throtA_val.addSpacing(5)
        hbox_layout_act_throtA_val.addWidget(self.singlelineEdit_act_throtA_val)
        
        # Create a horizontal layout for the button and line edit
        self.singlelineEdit_myRelPosAcc = QtWidgets.QLineEdit(readOnly=True)
        hbox_layout_myRelPosAcc = QHBoxLayout()
        hbox_layout_myRelPosAcc.addSpacing(5)
        line_edit_myRelPosAcc_1 = QLineEdit()
        line_edit_myRelPosAcc_1.setText("myRelPosAcc value:")
        line_edit_myRelPosAcc_1.setFixedWidth(300)
        hbox_layout_myRelPosAcc.addWidget(line_edit_myRelPosAcc_1)
        hbox_layout_myRelPosAcc.addSpacing(5)
        hbox_layout_myRelPosAcc.addWidget(self.singlelineEdit_myRelPosAcc)
        
        # Create a horizontal layout for the button and line edit
        self.singlelineEdit_actual_speed = QtWidgets.QLineEdit(readOnly=True)
        hbox_layout_actual_speed = QHBoxLayout()
        hbox_layout_actual_speed.addSpacing(5)
        line_edit_actual_speed_1 = QLineEdit()
        line_edit_actual_speed_1.setText("actual_speed value:")
        line_edit_actual_speed_1.setFixedWidth(300)
        hbox_layout_actual_speed.addWidget(line_edit_actual_speed_1)
        hbox_layout_actual_speed.addSpacing(5)
        hbox_layout_actual_speed.addWidget(self.singlelineEdit_actual_speed)
        
        # Create a horizontal layout for the button and line edit
        self.singlelineEdit_database_time = QtWidgets.QLineEdit(readOnly=True)
        hbox_layout_database_time = QHBoxLayout()
        hbox_layout_database_time.addSpacing(5)
        line_edit_database_time_1 = QLineEdit()
        line_edit_database_time_1.setText("database time:")
        line_edit_database_time_1.setFixedWidth(300)
        line_edit_database_time_2 = QLineEdit()
        hbox_layout_database_time.addWidget(line_edit_database_time_1)
        hbox_layout_database_time.addSpacing(5)
        hbox_layout_database_time.addWidget(self.singlelineEdit_database_time)
        
        # Create a horizontal layout for the button and line edit
        self.singlelineEdit_local_time = QtWidgets.QLineEdit(readOnly=True)
        hbox_layout_local_time = QHBoxLayout()
        hbox_layout_local_time.addSpacing(5)
        line_edit_local_time_1 = QLineEdit()
        line_edit_local_time_1.setText("local time:")
        line_edit_local_time_1.setFixedWidth(300)
        line_edit_local_time_2 = QLineEdit()
        hbox_layout_local_time.addWidget(line_edit_local_time_1)
        hbox_layout_local_time.addSpacing(5)
        hbox_layout_local_time.addWidget(self.singlelineEdit_local_time)
        
        # Create a horizontal layout for the button and line edit
        self.singlelineEdit_num_waypoints = QtWidgets.QLineEdit(readOnly=True)
        hbox_layout_num_waypoints = QHBoxLayout()
        hbox_layout_num_waypoints.addSpacing(5)
        line_edit_num_waypoints_1 = QLineEdit()
        line_edit_num_waypoints_1.setText("num waypoints:")
        line_edit_num_waypoints_1.setFixedWidth(300)
        line_edit_num_waypoints_2 = QLineEdit()
        hbox_layout_num_waypoints.addWidget(line_edit_num_waypoints_1)
        hbox_layout_num_waypoints.addSpacing(5)
        hbox_layout_num_waypoints.addWidget(self.singlelineEdit_num_waypoints)
        
        # Create and connect a combo box to select different route tables:
        hbox_layout_routeCombo = QHBoxLayout()
        hbox_layout_routeCombo.addSpacing(5)
        line_edit_routeCombo = QLineEdit()
        line_edit_routeCombo.setText("Select route:")
        line_edit_routeCombo.setFixedWidth(300)

        # Assuming you have a dictionary like this
        example_fetched_list_of_tables = {
            'key1': 'Route A',
            'key2': 'Route B',
            'key3': 'Route C'
        }

        # Create and connect a combo box to select different route tables:
        hbox_layout_routeCombo = QHBoxLayout()
        hbox_layout_routeCombo.addSpacing(5)
        line_edit_routeCombo = QLineEdit()
        line_edit_routeCombo.setText("Select route:")
        line_edit_routeCombo.setFixedWidth(300)
        self.routeCombo = QComboBox()
        # self.routeCombo.setFixedWidth(300)
        self.routeCombo.setStyleSheet(styleSheet_top_banner_combo_btn)
        # Get the values from the dictionary and add them to the QComboBox
        table_names = list(self.fetched_list_of_tables.values())
        self.routeCombo.addItems(table_names)
        self.routeCombo.activated.connect(self.selectRoute)
        hbox_layout_routeCombo.addWidget(line_edit_routeCombo)
        hbox_layout_routeCombo.addSpacing(5)
        hbox_layout_routeCombo.addWidget(self.routeCombo)
        
        ############################################################
        # self.singlelineEdit_ID = QtWidgets.QLineEdit(readOnly=True)
        # self.singlelineEdit_TIME = QtWidgets.QLineEdit(readOnly=True)
        # self.singlelineEdit_act_lat = QtWidgets.QLineEdit(readOnly=True)
        # self.singlelineEdit_act_lon = QtWidgets.QLineEdit(readOnly=True)
        # self.singlelineEdit_act_heading = QtWidgets.QLineEdit(readOnly=True)
        # self.singlelineEdit_act_steer_angle = QtWidgets.QLineEdit(readOnly=True)
        # self.singlelineEdit_act_throtA_val = QtWidgets.QLineEdit(readOnly=True)
        # self.singlelineEdit_myRelPosAcc = QtWidgets.QLineEdit(readOnly=True)
        self.singlelineEdit_8 = QtWidgets.QLineEdit(readOnly=True)
        # self.singlelineEdit_database_time = QtWidgets.QLineEdit(readOnly=True)
        # self.singlelineEdit_local_time = QtWidgets.QLineEdit(readOnly=True)
        self.singlelineEdit_11 = QtWidgets.QLineEdit(readOnly=True)
        self.singlelineEdit_12 = QtWidgets.QLineEdit(readOnly=True)
        self.singlelineEdit_13 = QtWidgets.QLineEdit(readOnly=True)
        self.singlelineEdit_14 = QtWidgets.QLineEdit(readOnly=True)
        self.singlelineEdit_15 = QtWidgets.QLineEdit(readOnly=True)
        self.singlelineEdit_16 = QtWidgets.QLineEdit(readOnly=True)
        self.singlelineEdit_17 = QtWidgets.QLineEdit(readOnly=True)
        self.singlelineEdit_18 = QtWidgets.QLineEdit(readOnly=True)
        self.singlelineEdit_19 = QtWidgets.QLineEdit(readOnly=True)
        self.singlelineEdit_20 = QtWidgets.QLineEdit(readOnly=True)
        self.singlelineEdit_21 = QtWidgets.QLineEdit(readOnly=True)
        self.singlelineEdit_22 = QtWidgets.QLineEdit(readOnly=True)
        # self.singlelineEdit_num_waypoints = QtWidgets.QLineEdit(readOnly=True)
        self.singlelineEdit_24 = QtWidgets.QLineEdit(readOnly=True)
        self.singlelineEdit_25 = QtWidgets.QLineEdit(readOnly=True)
        self.singlelineEdit_26 = QtWidgets.QLineEdit(readOnly=True)
        self.singlelineEdit_27 = QtWidgets.QLineEdit(readOnly=True)
        self.singlelineEdit_28 = QtWidgets.QLineEdit(readOnly=True)
        self.singlelineEdit_29 = QtWidgets.QLineEdit(readOnly=True)
        self.singlelineEdit_30 = QtWidgets.QLineEdit(readOnly=True)

        myFormLayout_LHS = QFormLayout()
        myFormLayout_LHS.setVerticalSpacing(1)
        myFormLayout_LHS.addRow(hbox_layout_refresh_routes_list)
        myFormLayout_LHS.addRow(hbox_layout_routeCombo)
        myFormLayout_LHS.addRow(hbox_layout_flip_route)
        myFormLayout_LHS.addRow(hbox_layout_add_route)
        myFormLayout_LHS.addRow(hbox_layout_del_waypoint)
        myFormLayout_LHS.addRow(hbox_layout_del_all_waypoints)
        myFormLayout_LHS.addRow(hbox_layout_clear_waypoint_crosses)
        myFormLayout_LHS.addRow(hbox_layout_del_table)
        myFormLayout_LHS.addRow(hbox_layout_new_route)
        myFormLayout_LHS.addRow(hbox_layout_ID)
        myFormLayout_LHS.addRow(hbox_layout_TIME)
        myFormLayout_LHS.addRow(hbox_layout_act_lat)
        myFormLayout_LHS.addRow(hbox_layout_act_lon)
        myFormLayout_LHS.addRow(hbox_layout_act_heading)
        myFormLayout_LHS.addRow(hbox_layout_act_steer_angle)
        myFormLayout_LHS.addRow(hbox_layout_act_throtA_val)
        myFormLayout_LHS.addRow(hbox_layout_myRelPosAcc)
        myFormLayout_LHS.addRow(hbox_layout_actual_speed)
        myFormLayout_LHS.addRow(hbox_layout_database_time)
        myFormLayout_LHS.addRow(hbox_layout_local_time)
        myFormLayout_LHS.addWidget(self.singlelineEdit_16)
        myFormLayout_LHS.addWidget(self.singlelineEdit_17)
        myFormLayout_LHS.addWidget(self.singlelineEdit_18)
        # myFormLayout_LHS.addWidget(self.clear_waypoint_crosses_btn)
        myFormLayout_LHS.addRow(hbox_layout_reset_database)
        # myFormLayout_LHS.addWidget(self.reset_database_btn)
        # myFormLayout_LHS.addWidget(self.send_main_coords_post_list_btn)
        myFormLayout_LHS.addRow(hbox_layout_main_coords_post)
        myFormLayout_LHS.addWidget(self.singlelineEdit_22)
        myFormLayout_LHS.addRow(hbox_layout_num_waypoints)
        myFormLayout_LHS.addWidget(self.singlelineEdit_24)
        myFormLayout_LHS.addWidget(self.singlelineEdit_25)
        myFormLayout_LHS.addRow(hbox_layout_test)
        myFormLayout_LHS.addWidget(self.singlelineEdit_28)
        myFormLayout_LHS.addWidget(self.singlelineEdit_29)
        row_4.addLayout(myFormLayout_LHS)
        
        self.setLayout(topLevelLayout)

        self.show()
        
    def parse_coordinates(self,data_string):
        """
        data format:
        des_lat:53.302759155331,des_lon:-4.2409339686008,des_lat:53.302747030784,des_lon:-4.2410767175252,

        Parses a string of comma-separated 'des_lat:X,des_lon:Y' coordinates
        into a list of [latitude, longitude] arrays.

        Args:
            data_string (str): The input string containing coordinate data.

        Returns:
            list: A list of lists, where each inner list contains a latitude
                  and longitude pair as floats.
        """
        # Clean up the string by removing any trailing commas
        # This specific method, strip(), only removes the characters specified in its argument from the beginning and end of the string.
        data_string = data_string.strip(',')
    
        # Split the string by the comma to get individual key:value pairs
        pairs = data_string.split(',')
    
        # Initialize an empty list to store the final coordinate arrays
        coordinates_list = []
    
        # Loop through the pairs with a step of 2 to process lat and lon together
        # This assumes the data is always in the des_lat, des_lon order
        for i in range(0, len(pairs), 2):
            try:
                # Extract latitude and longitude pairs
                lat_pair = pairs[i]
                lon_pair = pairs[i+1]
            
                # Split each pair by the colon and convert the value to a float
                lat_value = float(lat_pair.split(':')[1])
                lon_value = float(lon_pair.split(':')[1])
            
                # Append the new coordinate pair to the main list
                coordinates_list.append([lat_value, lon_value])
            except (IndexError, ValueError) as e:
                print(f"Skipping malformed data pair at index {i}: {e}")
                continue
                
        # Print the final result
        print("Parsed coordinates:")
        print(coordinates_list)

        return coordinates_list


    def selectRoute(self, index):
        # After the list of tables has been fetched, get a list of all the new variables and their values
        print("Now we can perform actions on the value selected. Here's the dictionary once more:")
        print("\nAll fetched variables:")
        for name, value in self.fetched_list_of_tables.items():
            print(f"{name}: {value}")

        # Get the text of the selected item using the index
        self.selected_route = self.routeCombo.itemText(index)
        print("Selected route = ", self.selected_route)
        # You could also get the current text directly
        # self.selected_route = self.routeCombo.currentText()
        
        print("Now download the coordinates for ", self.selected_route)
        # Format data as a dictionary for POST request:
        selected_route = {'selected_route': self.selected_route}

        url = "http://www.################database/select_table.php"
        headers = {"X-API-Password": passwords.get_password()}
        
        try:
            response = requests.post(url, data=selected_route, headers=headers)
            # If the server returns an error, print the exact message from PHP!
            if response.status_code != 200:
                print(f"\033[93mPHP Server says: {response.text}\033[0m")
            response.raise_for_status()  # Raise an exception for non-2xx status codes
            data_retreived = response.text
        except requests.exceptions.RequestException as e:
            print(f"Error fetching data: {e}")
        
        # Check for successful response
        if response.status_code == 200:
            print("data_retreived: ", data_retreived)
            self.fetched_coordinates_list = self.parse_coordinates(data_retreived)
            print("data coordinate data retreived: ", self.fetched_coordinates_list)
            line_colour = "y"
            self.draw_black_crosses(self.fetched_coordinates_list, line_colour) # TODO: not displaying all the crosses !! (There are 4 sets of coords in test1 table)
        else:
            print("Error sending data:", response.status_code)

        
    def clickMethod_1a(self):
        data_to_send = self.page1Line_1b_1.text()
        # self.writeData(data_to_send)
        print('Waypoints to WEEDINATOR: ' + data_to_send)
        
    def clickMethod_fetch_hist_coords(self):
        # send two variables to php script to give the required ID range to be downloaded:
        ID_from_value = self.page1Line_1b_2.text()
        ID_to_value = self.page1Line_1c_2.text()
        # a second text entry to help get the range required:
        # place_holder = self.page1Line_1b_2b.text()
        self.parse_downloaded_data_string(ID_from_value,ID_to_value)
        print('Historical coords to download: ' + ID_from_value)
        
    def clickMethod_throttleSliders(self):
        throttleASlider_value = str(self.throttleASlider.value())
        throttleBSlider_value = str(self.throttleBSlider.value())
        self.writeThrottleData(throttleASlider_value, throttleBSlider_value)
        print('throttleASlider_value: ' + throttleASlider_value)
        
    def clickMethod_create_route(self):
        data_to_send = self.line_edit_new_route_2.text()
        # Create a new table with the current main_coords_list
        url = "http://www.################database/create_table.php"
        self.writeData_to_database(data_to_send, url)
        print('create_route: ' + data_to_send + " ", url)
        print("Now try to clear all waypoints, crosses and lines not added to 'main':")
        self.clear_waypoint_crosses()
        
    def clickMethod_flip_route(self):
        # TODO: use self.clear_waypoint_crosses() instead of the below section:
        # Iterate through all objects on the axes
        for artist in list(self.ax.get_children()):
            # Check if the object is an annotation (which includes arrows from ax.annotate)
            if isinstance(artist, matplotlib.text.Annotation):
                artist.remove()

        self.annotation_object_1 = None
        self.annotation_object_2 = None
        
        print("self.fetched_coordinates_list: ",self.fetched_coordinates_list)
        print("self.hist_coords_list: ",self.hist_coords_list)
        
        num_to_flip = len(self.fetched_coordinates_list)
        print("num_to_flip 1: ",num_to_flip)
        if num_to_flip  >1:
            self.fetched_coordinates_list[-num_to_flip:] = self.fetched_coordinates_list[-num_to_flip:][::-1]
            line_colour = "y"
            # Redraw the lines and arrows:
            self.draw_black_crosses(self.fetched_coordinates_list, line_colour) # TODO: not displaying all the crosses !! (There are 4 sets of coords in test1 table)
            print("fetched_coordinates_list successfully reversed !!")

        num_to_flip = len(self.hist_coords_list)
        print("num_to_flip 2: ",num_to_flip)
        if num_to_flip  >1:
            self.hist_coords_list[-num_to_flip:] = self.hist_coords_list[-num_to_flip:][::-1]
            # Redraw the lines and arrows:
            line_colour = "r"
            self.draw_black_crosses(self.hist_coords_list, line_colour) # TODO: not displaying all the crosses !! (There are 4 sets of coords in test1 table)
            print("hist_coords_list successfully reversed !!")
        
    def clickMethod_del_all_waypoints(self):
        # Remove the last coordinate pair in the list:
        self.main_coords_list = []
        
        line_colour = "m"
        # TODO: remove the section below and replace with function: self.clear_waypoint_crosses()
        # Iterate through all objects on the axes
        for artist in list(self.ax.get_children()):
            # Check if the object is an annotation (which includes arrows from ax.annotate)
            if isinstance(artist, matplotlib.text.Annotation):
                artist.remove()
                
        self.annotation_object_1 = None
        self.annotation_object_2 = None

        # Delete the waypoint crosses:
        if (len(self.plot_objects_a) > 0) and (self.plot_objects_a is not None):
            for plot_object_a in self.plot_objects_a:
                try:
                    plot_object_a.remove()  # Call remove() directly on the plot object
                except:
                    pass
                    # print("Error encountered in removing plot object")
            print("Waypoint crosses have been cleared !!!! ")

        # Remove waypoint lines:    
        for i in range (len(self.ax.lines)):
            # Iterate through lines in the axes and remove the matching one:
            for line in self.ax.lines:
                try:
                    line.remove()
                except:
                    print("Error encountered in removing line object")
                # print("Waypoint line removed successfully!")
                break  # Exit the loop after successful removal

        print("Waypoint crosses and lines have been cleared !!!! ")

        self.draw_black_crosses(self.main_coords_list, line_colour)
        

    def clickMethod_del_waypoint(self):
        # Remove the last coordinate pair in the list:
        self.main_coords_list = self.main_coords_list[:-1]
        
        line_colour = "m"
            
        # Iterate through all objects on the axes
        for artist in list(self.ax.get_children()):
            # Check if the object is an annotation (which includes arrows from ax.annotate)
            if isinstance(artist, matplotlib.text.Annotation):
                artist.remove()
                
        self.annotation_object_1 = None
        self.annotation_object_2 = None

        # Delete the waypoint cross:
        '''
        if (len(self.plot_objects_a) > 0) and (self.plot_objects_a is not None):
            try:
                self.plot_object_a.remove()  # Call remove() directly on the plot object
            except:
                pass
                    # print("Error encountered in removing plot object")
        '''

        # Remove waypoint lines:
        # line.remove()

        # Delete the waypoint crosses:
        if (len(self.plot_objects_a) > 0) and (self.plot_objects_a is not None):
            for plot_object_a in self.plot_objects_a:
                try:
                    plot_object_a.remove()  # Call remove() directly on the plot object
                except:
                    pass
                    # print("Error encountered in removing plot object")
            print("Waypoint crosses have been cleared !!!! ")

        # Remove waypoint lines:    
        for i in range (len(self.ax.lines)):
            # Iterate through lines in the axes and remove the matching one:
            for line in self.ax.lines:
                try:
                    line.remove()
                except:
                    print("Error encountered in removing line object")
                # print("Waypoint line removed successfully!")
                break  # Exit the loop after successful removal

        print("Waypoint cross and line has been cleared !!!! ")

        self.draw_black_crosses(self.main_coords_list, line_colour)
        
    def clickMethod_add_route(self):
        # TODO: des_coords is a weird name for the table, should be more like 'main_coords'.
        print('Now add main crosses and send to the table "des_coords" having previously deleted all table rows: ')
        shortened_des_coords_list = self.des_coords_list[1:]
        print("len(shortened_des_coords_list): ",len(shortened_des_coords_list))
        print("len(self.fetched_coordinates_list): ",len(self.fetched_coordinates_list))

        if len(shortened_des_coords_list)>0:
            self.main_coords_list.extend(shortened_des_coords_list)
            del self.des_coords_list
            self.des_coords_list = [[None,None]]

        self.len_fetched_coordinates_list = len(self.fetched_coordinates_list)
        if self.len_fetched_coordinates_list >0:
            self.main_coords_list.extend(self.fetched_coordinates_list)
            del self.fetched_coordinates_list
            self.fetched_coordinates_list = []
            
        if len(self.hist_coords_list) >1:
            self.main_coords_list.extend(self.hist_coords_list)
            del self.hist_coords_list
            self.hist_coords_list = []

        print("Total extended data coordinate data retreived: ", self.main_coords_list)
        
        myData_json = json.dumps(self.main_coords_list)
        print("myData_json: ", myData_json)
        
        payload = {
            'coords_data': myData_json
        }

        url = "http://www.################database/des_coords.php"
        headers = {"X-API-Password": passwords.get_password()}
        response = requests.post(url, data=payload, headers=headers)

        if response.status_code != 200:
            print(f"\033[93mPHP Server says: {response.text}\033[0m")
        
        # Check for successful response
        if response.status_code == 200:
            # Delete the recently added crosses, but not the main ones:
            self.clear_waypoint_crosses()
            # print("Data sent successfully!")
            data_retreived = response.text
            print("data_retreived: ", data_retreived)
            line_colour = "m"
            
            # Iterate through all objects on the axes
            # TODO: self.clear_waypoint_crosses() now does the below, so delete this next section:
            for artist in list(self.ax.get_children()):
                # Check if the object is an annotation (which includes arrows from ax.annotate)
                if isinstance(artist, matplotlib.text.Annotation):
                    artist.remove()
                
            self.annotation_object_1 = None
            self.annotation_object_2 = None

            # self.ax.add_artist(self.ad)
            try:
                self.annotation_object_1.remove()
            except:
                pass
            try:
                self.annotation_object_2.remove()
            except:
                pass

            # 3. Redraw the canvas to update the plot
            # self.ax.figure.canvas.draw()

            self.draw_black_crosses(self.main_coords_list, line_colour)
        else:
            print("Error sending data:", response.status_code)
            
    def clickMethod_del_table(self):
        # Get the name of the table to be deleted from the selected route
        delete_table_name = self.selected_route

        # If no route is selected, do nothing.
        if not delete_table_name:
            msgBox = QMessageBox(self)
            msgBox.setWindowTitle('Selection Error')
            msgBox.setText("Please select a route to delete first.")
            
            # Unset the help button flag while keeping all others
            msgBox.setWindowFlags(msgBox.windowFlags() & ~QtCore.Qt.WindowContextHelpButtonHint)
            
            msgBox.setIcon(QMessageBox.Warning)
            msgBox.setStandardButtons(QMessageBox.Ok)
            msgBox.exec_()
            return

        # 1. Create a QMessageBox instance
        msgBox = QMessageBox(self)
        
        # Unset the help button flag while keeping all others
        msgBox.setWindowFlags(msgBox.windowFlags() & ~QtCore.Qt.WindowContextHelpButtonHint)
        
        # msgBox.setIcon(QMessageBox.Question)
        msgBox.setWindowTitle('Confirm Deletion')
        msgBox.setText(f"Are you sure you want to permanently delete the table '{delete_table_name}'?")
        msgBox.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msgBox.setDefaultButton(QMessageBox.No)

        # Note: there's already a global style sheet for the push button, but does not include the following:
        # TODO: the background of the button is still black !!
        myStylesheet = """
            QPushButton {
                font: 16pt;
                border: 2px solid black;
                border-radius: 5px;
                color: red;
                background-color: #b8eefc;
            }
            QPushButton::hover {
                background-color: lightgreen;
            }
            QMessageBox {
                background-color: yellow;
            }
            QMessageBox QLabel {
                background-color: yellow;
                color: red;
                min-width: 500px;
                font-size: 16px;
            }
            QMessageBox QPushButton {
                background-color: green;
                color: white; /* Changed button text to white for better contrast */
            }
            QMessageBox QPushButton:hover {
                background-color: darkgreen; /* Optional: Make the button a darker green when hovered over */
            }
        """
        # Find the buttons and apply the stylesheet
        for button in msgBox.findChildren(QPushButton):
            button.setStyleSheet(myStylesheet)

        msgBox.setStyleSheet(myStylesheet)
        
        # 3. Execute the dialog and get the user's reply
        reply = msgBox.exec_()

        # Check if the user clicked the 'Yes' button
        if reply == QMessageBox.Yes:
            # If 'Yes', proceed with the original code to send the POST request
            url = "http://www.################database/delete_table.php"
            headers = {"X-API-Password": passwords.get_password()}
            myUrl = url

            payload = {
                'delete_table_name': delete_table_name
            }

            # Define the blacklist
            black_list = ["control", "control_room", "weedinator"]

            # Check for blacklisted values in the payload
            if not any(value in black_list for value in payload.values()):
                # Send the POST request only if no blacklisted values are found
                response = requests.post(myUrl, data=payload, headers=headers)
                if response.status_code != 200:
                    print(f"\033[93mPHP Server says: {response.text}\033[0m")
                print("POST request sent successfully.")
            else:
                print("POST request was blocked due to a blacklisted value.")

            # Check for successful response
            try:
                if response.status_code == 200:
                    data_retreived = response.text
                    print(data_retreived)
                    self.clear_waypoint_crosses()
                else:
                    print("Error sending data:", response.status_code)
            except:
                print("No POST request was made.")
        else:
            # If user clicks 'No' or closes the dialog, do nothing.
            print("Deletion cancelled by user.")
        
    def writeData_to_database(self, data, url):
        print('We going to write this data to database:  ' + data +  " to this url: ", url)

        new_table_name = data

        # Send a POST request to the PHP script with the data
        myUrl = url
        #TODO: actual data to send will be: coords_list:
        
        # Using slicing to get all elements from index 1 to the end TODO: change des_coords_list to des_coords_list = []
        # Decide which coordinate list to upload:
        new_table_coords_list = []
        if len(self.des_coords_list)>1:
            new_table_coords_list.extend(self.des_coords_list[1:])
            del self.des_coords_list
            self.des_coords_list = [[None,None]]
            
        if len(self.hist_coords_list) >1:
            new_table_coords_list.extend(self.hist_coords_list)
            del self.hist_coords_list
            self.hist_coords_list = []
            
        if len(self.fetched_coordinates_list) >1:
            new_table_coords_list.extend(self.fetched_coordinates_list)
            del self.fetched_coordinates_list
            self.fetched_coordinates_list = []
            
        if len(self.main_coords_list) >1:
            new_table_coords_list.extend(self.main_coords_list)
            # No need to delete self.main_coords_list.

        myData_json = json.dumps(new_table_coords_list)
        print("new_table_coords_list: ", new_table_coords_list)
        print("myData_json: ", myData_json)
        
        payload = {
            'new_table_name': new_table_name,
            'coords_data': myData_json
        }

        # Send the POST request
        headers = {"X-API-Password": passwords.get_password()}
        try:
            response = requests.post(myUrl, data=payload, headers=headers)
            # If the server returns an error, print the exact message from PHP!
            if response.status_code != 200:
                print(f"\033[93mPHP Server says: {response.text}\033[0m")
            response.raise_for_status()  # Raise an exception for non-2xx status codes
            data_retreived = response.text
        except requests.exceptions.RequestException as e:
            print(f"Error fetching data: {e}")
        
        # myData = {'myData': new_table_name}  # Format data as a dictionary for POST request
        #TODO: can i add myData_json to myData?

        # Check for successful response
        if response.status_code == 200:
            print(data_retreived)
            self.clear_waypoint_crosses()
        else:
            print("Error sending data:", response.status_code)


    def writeThrottleData(self, throttleA_value, throttleB_value):
        # Send a POST request to the PHP script with the data
        url = "http://www.################database/control_01.php"
        headers = {"X-API-Password": passwords.get_password()}

        data_list = [["", ""], ["", ""]]
        data_list[0][0] = "throttAVal"
        data_list[0][1] = throttleA_value
        data_list[1][0] = "throttBVal"
        data_list[1][1] = throttleB_value
        myData_json = json.dumps(data_list)
        
        payload = {
            'myData_json': myData_json
        }

        response = requests.post(url, data=payload, headers=headers)
        if response.status_code != 200:
            print(f"\033[93mPHP Server says: {response.text}\033[0m")

        # Check for successful response
        if response.status_code == 200:
            # print("Data sent successfully!")
            data_retreived = response.text
            print(data_retreived)
        else:
            print("Error sending data:", response.status_code)
            
    def parse_downloaded_data_string(self,ID_from_value,ID_to_value): # send two variables to php script to give the required ID range to be downloaded:
        #TODO: ID_from_value needs to be sent to the php script.
        # url = 'http://www.################database/show_data_simple.php'

        print("ID_from_value: ",ID_from_value)
        print("ID_to_value: ",ID_to_value)
        
        # Send a POST request to the PHP script with the data
        #TODO: check this php file for how to handle the outgoing data: url = "http://www.################database/control_01.php"
        # Do an initial test with control table and show_data_simple_02.php:
        url = 'http://www.################database/show_data_simple_02.php'
        headers = {"X-API-Password": passwords.get_password()}
        
        #TODO: create better names for the below, which are used in table 'control':
        
        # Format data as a dictionary for POST request:
        GSM_session_data = {
            'ID_from_value': ID_from_value,
            'ID_to_value': ID_to_value
        }

        response = requests.post(url, data=GSM_session_data, headers=headers)
        if response.status_code != 200:
            print(f"\033[93mPHP Server says: {response.text}\033[0m")

        # Check for successful response
        if response.status_code == 200:
            # print("Data sent successfully!")
            data_retreived = response.text
            print("data_retreived: ",data_retreived)
        else:
            print("Error sending data:", response.status_code)
        
        '''
        # The input data string
        data_string = 'ID:5504act_lat:53.302657712act_lon:-4.239859107?ID:5503act_lat:53.302657909act_lon:-4.239859029?ID:5502act_lat:53.302657668act_lon:-4.239860338?ID:5501act_lat:53.302657493act_lon:-4.23986146?ID:5500act_lat:53.302657232act_lon:-4.239863898?ID:5499act_lat:53.30265685act_lon:-4.239867347?ID:5498act_lat:53.302657783act_lon:-4.239866888?ID:5497act_lat:53.302658903act_lon:-4.239866019?ID:5496act_lat:53.302660165act_lon:-4.239865396?ID:5495act_lat:53.302660405act_lon:-4.239864357?'

        data_string = 'ID:105act_lat:53.30263520act_lon:-4.23985540myRelPosAcc:0?ID:104act_lat:999.00000000act_lon:999.00000000myRelPosAcc:0?ID:102act_lat:53.30261800act_lon:-4.23985080myRelPosAcc:0?ID:101act_lat:53.30262670act_lon:-4.23986660myRelPosAcc:0?ID:100act_lat:53.30264680act_lon:-4.23988820myRelPosAcc:0?'

        
# Sample data_string including the new 'myRelPosAcc' field
data_string = 'ID:105act_lat:53.30263520act_lon:-4.23985540myRelPosAcc:0?ID:104act_lat:999.00000000act_lon:999.00000000myRelPosAcc:0?ID:102act_lat:53.30261800act_lon:-4.23985080myRelPosAcc:0?ID:101act_lat:53.30262670act_lon:-4.23986660myRelPosAcc:0?ID:100act_lat:53.30264680act_lon:-4.23988820myRelPosAcc:0?'
        '''
        data_string = data_retreived
        
        # Initialize an empty list to store the extracted dictionaries
        extracted_data = []

        # Split the data string into individual records using '?' as the delimiter
        # Using .strip() to remove any leading/trailing whitespace from each record
        records = [record.strip() for record in data_string.split('?') if record.strip()]

        # Iterate over each record to extract the values
        for record_str in records:
            # Create a dictionary to hold the data for the current record
            current_record = {}

            # Extract ID
            parts_id = record_str.split('ID:')
            if len(parts_id) > 1:
                id_and_rest = parts_id[1]
        
                # Find the end of the ID by looking for 'act_lat:'
                lat_start_index = id_and_rest.find('act_lat:')
                if lat_start_index != -1:
                    current_record['ID'] = int(id_and_rest[:lat_start_index])
                    remaining_str = id_and_rest[lat_start_index:]
                else:
                    # If 'act_lat:' is not found, try to find 'myRelPosAcc:'
                    myrelposacc_start_index = id_and_rest.find('myRelPosAcc:')
                    if myrelposacc_start_index != -1:
                        current_record['ID'] = int(id_and_rest[:myrelposacc_start_index])
                        remaining_str = id_and_rest[myrelposacc_start_index:]
                    else:
                        current_record['ID'] = int(id_and_rest)
                        remaining_str = ""
            else:
                continue # Skip if ID is not found in the expected format

            # Extract act_lat and act_lon if remaining_str exists
            if remaining_str:
                parts_lat = remaining_str.split('act_lat:')
                if len(parts_lat) > 1:
                    lat_and_rest = parts_lat[1]
                    parts_lon = lat_and_rest.split('act_lon:')
                    if len(parts_lon) > 1:
                        current_record['act_lat'] = float(parts_lon[0])
                
                        # Now, from the part after 'act_lon:', we need to separate lon from myRelPosAcc
                        lon_and_myrelposacc = parts_lon[1]
                        myrelposacc_start_index = lon_and_myrelposacc.find('myRelPosAcc:')
                
                        if myrelposacc_start_index != -1:
                            current_record['act_lon'] = float(lon_and_myrelposacc[:myrelposacc_start_index])
                            # The remainder is the myRelPosAcc part
                            myrelposacc_str = lon_and_myrelposacc[myrelposacc_start_index:]
                        else:
                            # If myRelPosAcc is not found, the rest is just act_lon
                            current_record['act_lon'] = float(lon_and_myrelposacc)
                            myrelposacc_str = "" # No myRelPosAcc to parse
                    elif len(parts_lon) == 1:
                        current_record['act_lat'] = float(parts_lon[0])
                        current_record['act_lon'] = None
                        myrelposacc_str = ""
                    else:
                        current_record['act_lat'] = None
                        current_record['act_lon'] = None
                        myrelposacc_str = ""
                else:
                    current_record['act_lat'] = None
                    current_record['act_lon'] = None
                    myrelposacc_str = remaining_str # If no lat/lon, myRelPosAcc might be here

            # Extract myRelPosAcc from myrelposacc_str if it exists
            if 'myRelPosAcc:' in myrelposacc_str:
                parts_myrelposacc = myrelposacc_str.split('myRelPosAcc:')
                if len(parts_myrelposacc) > 1:
                    try:
                        current_record['myRelPosAcc'] = float(parts_myrelposacc[1])
                    except ValueError:
                        current_record['myRelPosAcc'] = None # Handle cases where conversion to int fails
                else:
                    current_record['myRelPosAcc'] = None
            else:
                current_record['myRelPosAcc'] = None
            
            # Add the parsed record to the list
            extracted_data.append(current_record)

        print("Now print the extracted data to verify:")
        for item in extracted_data:
            print(item)

                # You can now access the data, for example:
                # print(extracted_data[0]['ID'])
                # print(extracted_data[1]['act_lat'])
        #TODO: now use: def draw_black_crosses(self,coords_list) function to draw black crosses:
        # Initialize an empty list to store the coordinates
        
        del self.hist_coords_list
        self.hist_coords_list = []

        # Iterate through each dictionary in extracted_data
        for record in extracted_data:
            # Check if 'act_lat' and 'act_lon' keys exist and are not None
            if 'act_lat' in record and record['act_lat'] is not None and \
               'act_lon' in record and record['act_lon'] is not None:
        
                # Append a tuple (or a list) of (latitude, longitude) to coords_list
                # Using a tuple is generally good for fixed pairs like coordinates
                self.hist_coords_list.append((record['act_lat'], record['act_lon']))
            else:
                # Optional: Print a message or handle records with missing coordinates
                print(f"Skipping record ID {record.get('ID', 'N/A')} due to missing/None coordinates.")

        # Print the new coords_list to verify
        print("\n--- self.hist_coords_list ---")
        for coord_pair in self.hist_coords_list:
            print(coord_pair)

        print(f"\nTotal coordinate pairs: {len(self.hist_coords_list)}")
        line_colour = "r"
        self.draw_black_crosses(self.hist_coords_list, line_colour)

    #TODO: delete this duplicate function:
    '''
    def readData(self):
        print('We going to try to download a load of historical data from the weedinator table:  ' + data)
        GSM_session_num = data

        # Send a POST request to the PHP script with the data
        url = "http://www.################database/show_data.php"  # Replace with your actual URL
        GSM_session_data = {'GSM_session_data': GSM_session_num}  # Format data as a dictionary for POST request

        response = requests.post(url, data=GSM_session_data)

        # Check for successful response
        if response.status_code == 200:
            # print("Data sent successfully!")
            data_retreived = response.text
            print(data_retreived)
        else:
            print("Error sending data:", response.status_code)
    '''
    
    def connectToSerialPort(self):
        self.serial.setPortName('ttyACM0')
        # self.serial.setPortName('ttyAMA0')
        self.serial.setBaudRate(115200)
        self.serial.open(QtCore.QIODevice.ReadWrite)
        print("Trying to connect to serial .... ")
        
    def switchPage(self):
        self.stackedLayout.setCurrentIndex(self.pageCombo.currentIndex())
        
    # When serial data comes in, a QT slot called 'receive' is engaged where parsing of data occurrs.
    def __receiveSerial(self):
        self.serial = QtSerialPort.QSerialPort(self, readyRead=self.receive)
        
       

    # ID:5504TIME:1753701380act_lat:53.302657712act_lon:-4.239859107act_heading:333.96act_steer_angle:15.5act_throtA_val:250sig_str:0myRelPosAcc:0.051

    # Get a single line of the latest data:
    def database_parsing(self): # Called by a timer/poller set in def --init--
        self.my_busy_flag_02 = True
        print("Trying to read database ... ")

        try:
            with urllib.request.urlopen('http://www.################database/show_data_min.php') as f:
                myData = f.read().decode('utf-8')
                print(myData)
                self.box_weed_database_line.setText(str(myData))
                myData = myData + ",null:123"  # add some dummy dataso that last chunk of real data gets processed.
                size = len(myData)
              
            digi_detect = False
            char_detect = False
        
            myString = []
            newstring = ""
            count= 0
            serialAvailable = "TRUE"
            #TODO: replace the following try with dict based parsing:
            try:
                for j in range(size):
                    c = myData[j]
                    # Finally, check for all digit related stuff, make the new string and increment counter.  
                    if  c.isdigit() == False and c != '.' and c != '-' and char_detect == True and digi_detect == True:
                        myString.append(newstring)
                        # print("newstring:",newstring)
                        newstring = ""
                        count+= 1
                        digi_detect = False
                        char_detect = False
                    # Add a space instead of colon for legibility, then remove colon in next step:
                    if c == ':':
                        # newstring+= '= '
                        char_detect = True
                    # Check that c is not digits, decimal place, minus signs or colon and add to current string:
                    if c.isdigit() == False and c != '.' and c != '-' and c != ':':
                        # newstring+= c
                        char_detect = True
                    # Check for digits, decimal place and minus signs once more:
                    if c.isdigit() == True or c == '.' or c == '-':
                        newstring+= c
                        digi_detect = True
            except:
                serialAvailable = "FALSE"
            if len(myString) > 0:
                pass
                # print("myString: ",myString)
            try:
                myString[0] = myString[0].strip()
                self.singlelineEdit_ID.setText(myString[0])  # ID
                self.singlelineEdit_TIME.setText(myString[1])  # UNIX time
                self.singlelineEdit_act_lat.setText(myString[2])  # act_lat
                self.singlelineEdit_act_lon.setText(myString[3])  # act_lon
                self.singlelineEdit_act_heading.setText(myString[4])  # act_heading
                self.singlelineEdit_act_steer_angle.setText(myString[5])  # act_steer_angle
                self.singlelineEdit_act_throtA_val.setText(myString[6])  # act_throtA_val
                # self.singlelineEdit_myRelPosAcc.setText(myString[7])  # sig_str
                self.singlelineEdit_myRelPosAcc.setText(myString[9])  # myRelPosAcc
                self.singlelineEdit_actual_speed.setText(myString[8]) # actual_speed
                # print("Check the GPS and heading values:")
                self.act_lat_float, self.act_lat_string = self.get_values_from_myString(myString[2])
                self.act_lon_float, self.act_lon_string = self.get_values_from_myString(myString[3])
                self.act_heading_float, self.act_heading_string = self.get_values_from_myString(myString[4])
                self.act_steer_angle_float, self.act_steer_angle_string = self.get_values_from_myString(myString[5])
                '''
                print("############################################################################")
                print("myString[7]: ", myString[7])
                print("myString[8]: ", myString[8])
                print("myString[9]: ", myString[9])
                print("############################################################################")
                '''
            except:
                pass
                



            # Get current Unix timestamp
            x,y = self.get_values_from_myString(myString[1])
            timestamp = int(x)
            # Get current Unix timestamp
            timestamp = time.time()

            # Convert timestamp to local time structure
            local_time = time.localtime(timestamp)

            # Extract month, day, hour, minute, and second
            month_number = local_time.tm_mon
            day_number = local_time.tm_mday
            hour = local_time.tm_hour
            minute = local_time.tm_min
            second = local_time.tm_sec

            # Convert month number to short text format (Jan, Feb, ...)
            month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                           "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
            month_text = month_names[month_number - 1]

            # Convert day number to short text format (Sat, Sun, ...)
            day_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
            day_text = day_names[local_time.tm_wday]

            # Print the formatted date and time
            # print(f"{month_text} {day_text:02d}, {hour:02d}:{minute:02d}:{second:02d}")

            myTimeString = month_text + ", " + day_text + " " + str(hour) + ":" + str(minute) + ":" + str(second)

            # Get last database Unix timestamp
            x,y = self.get_values_from_myString(myString[1])
            myTimeStamp = int(x)
            myTimeString = self.readableDateTime(myTimeStamp)
            self.singlelineEdit_database_time.setText(myTimeString)
            
            # Get current Unix timestamp
            myTimeStamp = time.time()
            myTimeString = self.readableDateTime(myTimeStamp)
            self.singlelineEdit_local_time.setText(myTimeString)

                
            # print("GPS coords: " + str(self.act_lat_float)  + " , " + str(self.act_lon_float))
            # print("Heading: " + str(self.act_heading_float))

        except urllib.error.URLError as e:
           print(e.reason)
        self.my_busy_flag_02 = False
           
    def readableDateTime(self, myTimeStamp):

        # Convert timestamp to local time structure
        local_time = time.localtime(myTimeStamp)

        # Extract month, day, hour, minute, and second
        month_number = local_time.tm_mon
        day_number = local_time.tm_mday
        hour = local_time.tm_hour
        minute = local_time.tm_min
        second = local_time.tm_sec

        # Convert month number to short text format (Jan, Feb, ...)
        month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                       "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        month_text = month_names[month_number - 1]

        # Convert day number to short text format (Sat, Sun, ...)
        day_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        day_text = day_names[local_time.tm_wday]

        myTimeString = month_text + ", " + day_text + " " + str(hour) + ":" + str(minute) + ":" + str(second)
        return myTimeString
    
    
    
           
    def get_values_from_myString(self, myString):
        # Check for digits, decimal place and minus signs once more:
        newstring_digits = ""
        newstring_letters = ""
        count= 0
        size = len(myString)
        for j in range(0,size):
            c = myString[j]
            if c.isdigit() == True or c == '.' or c == '-':
                newstring_digits+= c
            else:
                newstring_letters+= c
        digits_float = float(newstring_digits)
        letters_string = newstring_letters

        # print("letters_string: ",letters_string)
        # print("digits_float: ", digits_float)
        try:letters_string = letters_string.strip()
        except:letters_string = ""

        return digits_float, letters_string

       
    def create_array_for_graphs(self, myArray, myString):
        # Check for digits, decimal place and minus signs once more:
        newstring_digits = ""
        newstring_letters = ""
        count= 0
        size = len(myString)
        for j in range(0,size):
            c = myString[j]
            if c.isdigit() == True or c == '.' or c == '-':
                newstring_digits+= c
            else:
                newstring_letters+= c
        digits_float = float(newstring_digits)
        letters_string = newstring_letters

        print("letters_string: ",letters_string)
        print("digits_float: ", digits_float)
        try:letters_string = letters_string.strip()
        except:letters_string = ""
        myArray.append(digits_float)
        if len(myArray) > 500:
            # remove the first element in the list:
            myArray = myArray[1:]
        return myArray
        
    def connectToSerialPort(self):
        self.serial.setPortName('ttyACM0')
        # self.serial.setPortName('ttyAMA0')
        self.serial.setBaudRate(115200)
        self.serial.open(QtCore.QIODevice.ReadWrite)
        print("Trying to connect to serial .... ")
        
    def on_map_click(self, event):
        if (self.my_busy_flag_01 == False) and (self.my_busy_flag_02 == False) and (self.my_busy_flag_03 == False) and (self.my_busy_flag_04 == False):
            x, y = event.xdata, event.ydata
            crs_out = CRS.from_epsg("4326")  # webGPS
            crs_in = CRS.from_epsg("3857")   # Mercator
            transformerB = Transformer.from_crs(crs_in, crs_out)
            print("on_map_click results:")
            print(x, ",", y)
            webGPS = transformerB.transform(x, y)
            print(webGPS[0], ",", webGPS[1])
            results = str(x) + "," +str(y) + " , " + str(webGPS[0]) + "," + str(webGPS[1])
            clicked_des_lat = webGPS[0]
            clicked_des_lon = webGPS[1]
            self.mouse_click_data.setText(results)
            # New row to be appended (latitude, longitude)
            new_row = [clicked_des_lat , clicked_des_lon]
            # Append the new row to the list using the append() method
            self.des_coords_list.append(new_row)
            print(self.des_coords_list)
            return clicked_des_lat, clicked_des_lon
            
            # Refresh map_canvas
            self.map_canvas.draw()
            self.my_busy_flag_01 = False
        else:
            print("WARNING: A BUSY FLAG WAS WAVED !!")


    def send_main_coords_post_list(self):
        self.my_busy_flag_03 = True
        # Define desired latitude and longitude:
        '''
        main_coords_list = [
            ["53.30285138837834", "-4.241074543683688"],
            ["53.302712822223086", "-4.241236132567598"],
            ["53.30253485065781", "-4.241457864399331"]
        ]
        '''

        # Delete the first row using slicing or else it contains "NONE","NONE"
        #TODO: Currently only sends one line of data - change this function and also control_room_database/send.php -> control_room table. Copy function 'def clickMethod_add_route(self):' and 'database/des_coords.php' using control_room table.

        print("main_coords_list to send to control_room table: ", self.main_coords_list)
        
        myData_json = json.dumps(self.main_coords_list)
        print("myData_json: ", myData_json)
        
        payload = {
            'coords_data': myData_json
        }

        # Base URL:
        url = "http://www.################control_room_database/send.php?"
        headers = {"X-API-Password": passwords.get_password()}
        
        response = requests.post(url, data=payload, headers=headers)
        if response.status_code != 200:
            print(f"\033[93mPHP Server says: {response.text}\033[0m")
        
        # Check for successful response
        if response.status_code == 200:
            # Delete the recently added crosses, but not the main ones:
            self.clear_waypoint_crosses()
            # print("Data sent successfully!")
            data_retreived = response.text
            print("data_retreived: ", data_retreived)
        else:
            print("Error sending data:", response.status_code)
        self.my_busy_flag_03 = False
        
    def parse_fetched_table_names(self,data):
        # data = 'control?control_room?control_room_test_apr_21?glasshouse?test1?weedinator?'

        # Remove the trailing '?' if it exists
        if data.endswith('?'):
            data = data[:-1]

        # Split the string into a list of strings
        data_list = data.split('?')

        # Create a dictionary to hold the new variables
        self.fetched_list_of_tables = {}

        # Loop through the list and assign a new variable name to each item
        for i, item in enumerate(data_list):
            variable_name = f'fetched_{i+1}'
            self.fetched_list_of_tables[variable_name] = item

        # You can also get a list of all the new variables and their values
        print("\nAll fetched variables:")
        for name, value in self.fetched_list_of_tables.items():
            print(f"{name}: {value}")
        # Now update the combo box:
        self.updateRouteCombo(self.fetched_list_of_tables)
        
    def fetch_routes_list(self):
        self.my_busy_flag_03 = True
        print("Trying to fetch a list of tables in main Weedinator database: database.... ")
        # Base URL
        url_base = "http://www.################database/fetch_table_list.php"
        headers = {"X-API-Password": passwords.get_password()}

        # del self.des_coords_list[0]
        # Send POST request with data
        try:
            response = requests.post(url_base,headers=headers)
            # If the server returns an error, print the exact message from PHP!
            if response.status_code != 200:
                print(f"\033[93mPHP Server says: {response.text}\033[0m")

            response.raise_for_status()  # Raise an exception for non-2xx status codes
            print("Table data successfully fetched:")
            data_retreived = response.text
            print(data_retreived)
        except requests.exceptions.RequestException as e:
            print(f"Error fetching data: {e}")
            
        # Now parse the data:
        self.parse_fetched_table_names(data_retreived)
        
        self.my_busy_flag_03 = False
        
    def updateRouteCombo(self, new_data):
        """
        Clears the existing QComboBox items and adds new ones from a data source.
        :param new_data: A list of strings to populate the combo box with.
        """
        print("Here is the fetched table names dictionary: ")
        for name, value in new_data.items():
            print(f"{name}: {value}")
        # 1. Clear the old items
        self.routeCombo.clear()
    
        # 2. Add the new items from the provided data
        #TODO: the new items are currently the keys ie fetched_1, fetched_2 etc and we need the values to be displayed, not the keys.
        if new_data:
            self.routeCombo.addItems(new_data.values())
        #TODO: Maybe need to send the keys as well in the above, but does not seem to be necessary !!


    def clear_waypoint_crosses(self):
        del self.des_coords_list
        self.des_coords_list = [[None,None]] #TODO: change this to [], but also change the code to remove the nones !!
        self.fetched_coordinates_list = []
        # TODO: also  delete self.hist_coords_list as above.
        
        # Iterate through all objects on the axes and clear arrow annotations:
        for artist in list(self.ax.get_children()):
            # Check if the object is an annotation (which includes arrows from ax.annotate)
            if isinstance(artist, matplotlib.text.Annotation):
                artist.remove()

        # Delete the waypoint crosses:
        if (len(self.plot_objects_a) > 0) and (self.plot_objects_a is not None):
            for plot_object_a in self.plot_objects_a:
                try:
                    plot_object_a.remove()  # Call remove() directly on the plot object
                except:
                    pass
                    # print("Error encountered in removing plot object")
            print("Waypoint crosses have been cleared !!!! ")

        # Remove waypoint lines:    
        for i in range (len(self.ax.lines)):
            # Iterate through lines in the axes and remove the matching one:
            for line in self.ax.lines:
                try:
                    line.remove()
                except:
                    print("Error encountered in removing line object")
                # print("Waypoint line removed successfully!")
                break  # Exit the loop after successful removal

        # Redraw the lines and arrows:
        line_colour = 'm'
        self.draw_black_crosses(self.main_coords_list, line_colour)

        # Refresh map_canvas
        self.map_canvas.draw()
        self.my_busy_flag_01 = False
            
        
    def reset_database(self):
        self.my_busy_flag_04 = True
        # Base URL
        url = "http://www.################control_room_database/delete_all_rows.php"
        headers = {"X-API-Password": passwords.get_password()}
        
        # Send request:
        try:
            response = requests.post(url, headers=headers)
            if response.status_code != 200:
                print(f"\033[93mPHP Server says: {response.text}\033[0m")
            response.raise_for_status()  # Raise an exception for non-2xx status codes
            print("Operation successfull!")
        except requests.exceptions.RequestException as e:
            print(f"Error sending data: {e}")
        
        print("Trying to reset control room database.... ")
        self.my_busy_flag_04 = False

        
QSS = """
QPushButton {
    background-color: yellow;
    color: magenta;
}

/* QSlider --------------------------------------  */
QSlider::groove:horizontal {
    border-radius: 1px;
    height: 3px;
    margin: 0px;
    background-color: rgb(52, 59, 72);
}
QSlider::groove:horizontal:hover {
    background-color: rgb(55, 62, 76);
}
QSlider::handle:horizontal {
    background-color: rgb(85, 170, 255);
    border: none;
    height: 40px;
    width: 40px;
    margin: -20px 0;
    border-radius: 20px;
    padding: -20px 0px;
}
QSlider::handle:horizontal:hover {
    background-color: rgb(155, 180, 255);
}
QSlider::handle:horizontal:pressed {
    background-color: rgb(65, 255, 195);
}
"""
        
def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(QSS)
    win = MainWindow()
    win.show()
    app.exec_()


if __name__ == '__main__':
    sys.exit(main())

