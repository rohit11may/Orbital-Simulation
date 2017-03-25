# Orbital Simulation Practical Project
# Rohit Prasad
# 2016-2017
# Last changed on 25/03/2016

# == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == ==
# Library Imports and Constants
# == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == ==

# == == ==
# GUI
# == == ==

from PyQt4.QtGui import *
from PyQt4.QtCore import Qt
from PyQt4.QtCore import pyqtSlot
from PyQt4.uic import loadUiType
from matplotlib.backends.backend_qt4agg import (
    FigureCanvasQTAgg as FigureCanvas,
    NavigationToolbar2QT as NavigationToolbar)

# == == ==
#  Multiprocessing and GUI Threading modules
# == == ==

from multiprocessing import Process, Manager, Value
from multiprocessing.sharedctypes import Value as cValue
from ctypes import c_double

# == == ==
#  Plotting library (MatPlotLib)
# == == ==

import matplotlib.animation as animation
from matplotlib.figure import Figure

# == == ==
#  Local Files
# == == ==

from src.body import Body
from src.orbitmath import calculate_resultant_force
from src.other import changeTextColour
from src.other import mergeSort

# == == ==
#  Others
# == == ==

import sys
import logging
import re

# == == ==
# CONSTANTS
# == == ==

AU = 149598e6 # DISTANCE FROM EARTH TO SUN
RED = '#ff0000'
BLUE = '#0000ff'
GREEN = '#00ff00'

# Setup logging to log files to aid in debugging.
logging.basicConfig(format='%(asctime)s.%(msecs)03d // %(message)s',
                    filename="..//logs//logfile.log",
                    datefmt='%H:%M:%S',
                    filemode='w',
                    level=logging.DEBUG)


# == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == ==
# GUI SETUP
# == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == ==

Ui_MainWindow, QMainWindow = loadUiType('..//GUI//window.ui')  # Load UI file from GUI folder.
UI_BodyConfigMainWindow, BodyConfigMainWindow = loadUiType(
    '..//GUI//body_config_widget.ui')  # Load config UI file from GUI folder.
UI_BodyStatsMainWindow, BodyStatsMainWindow = loadUiType(
    '..//GUI//body_stats_widget.ui')  # Load stats widget UI file from GUI folder.

class BodyConfig(BodyConfigMainWindow, UI_BodyConfigMainWindow):  # Setup config UI class for use in GUI
    def __init__(self):
        super(BodyConfig, self).__init__()
        self.setupUi(self)

class BodyStats(BodyStatsMainWindow, UI_BodyStatsMainWindow):  # Setup Stats UI class for use in GUI
    def __init__(self):
        super(BodyStats, self).__init__()
        self.setupUi(self)

'''
The above section loads parts of the GUI into 3 sets of classes.
 -  Ui_MainWindow, QMainWindow are the classes for the main window.
 -  Separate to Ui_MainWindow and QMainWindow, there is UI_BodyConfigMainWindow and BodyConfigMainWIndow which are
    the classes for the body configuration cards spawned on click of the 'Create New Body' button (dynamic generation
    of objects).
 -  Similarly, there is BodyStats and BodyStatsMainWindow which are the classes for the body statistics
    cards in the stats pane of the software.
 -  BodyConfig is the class that is used to instantiate an instance of a configuration card, hence it inherits from
    BodyConfigMainWindow and UI_BodyConfigMainWindow.
 -  Similarly, BodyStats is used to instantiate an instance of a statistics card for a body in the Stats pane and it
    inherits from BodyStatsMainWindow, UI_BodyStatsMainWindow.
'''

# == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == ==
# DATABASE CRUD HANDLERS
# == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == ==

# == == ==
# CREATE/UPDATE
# == == ==
def saveToDatabase(name, mass, position, velocity, type, simulate):
    '''
    Save's a body's details to the flatfile database and then refresh the GUI.
    '''
    db_read = open("..//lib//body_db.db", 'r') # Open file in read mode to check for duplicates
    for line in db_read.readlines(): # read line by line
        if line.rstrip().split(';')[0] == name: # remove line breaks, split by ;, take first item
            db_read.close() # close file because duplicate found
            return "Body with same name already in database!" # return log message
    db_read.close() # close read file because no duplicates found
    write_line = "{};{};{};{};{}\n".format(str(name),
                                           str(mass),
                                           (str(position[0]), str(position[1])),
                                           (str(velocity[0]), str(velocity[1])),
                                           str(type)) # format the line to be written

    db = open("..//lib//body_db.db", 'a') # open file in append mode
    db.write(write_line) # write the line to the end of the file
    db.close() # close the file
    simulate.setUpDB() # Refresh db in GUI.
    simulate.log("{} saved to DB!".format(name))
    return "Body Saved to DB!" # return log message

# == == ==
# DELETE
# == == ==
def deleteFromDatabase(name):
    '''
    Deletes the item corresponding to the given name, from the flatfile database .
    '''
    db_read = open("..//lib//body_db.db", 'r')  # Open file in read mode to check for duplicates
    db_copy = []
    for line in db_read.readlines():  # read line by line
        if line.split(';')[0] != name:  # remove line breaks, split by ;, take first item
            db_copy.append(line)
    db_read.close()  # close read file because no duplicates found
    db_write = open("..//lib//body_db.db", 'w')  # Open file in read mode to check for duplicates
    for line in db_copy:
        db_write.write(line)
    db_write.close()
    return "{} Deleted.".format(name)

# == == ==
# READ
# == == ==
def readFromDatabase():
    '''
    Reads data from the flatfile database sequentially.
    '''
    db_read = open("..//lib//body_db.db", 'r')  # Open file in read mode to check for duplicates
    data = []
    for line in db_read.readlines():
        datum = line.rstrip().split(';')
        data.append(datum)
    return data

'''
The above code handles the IO for the database:
-   saveToDatabase() creates items in the flatfile database, first by checking if it already exists in a similar form
    and rejecting the save command if so. It stores the name, position, mass, velocity and type of object so these
    can be loaded from the library pane in the GUI.
-   deleteFromDatabase() removes a record from the flatfile, given its name.
-   readFromDatabase() is used to load up the database sequentially by the library pane in the GUI.
'''

# == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == ==
# ORBITAL DATA GENERATION AND OUTPUT
# == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == ==

# == == ==
# DATA GENERATION
# == == ==
def generate(bodies, positionData, data_gen_pause, data_gen_stop, dt):
    '''
    Generates position data given a list of bodies while the simulation is not paused or stopped. Run in a separate
    thread to the plotting functions.
    '''
    while data_gen_stop.value == 1:  # If the stop flag (multiprocessing value) equals 1, repeat forever.
        if data_gen_pause.value == 1:  # If the pause flag equals 1, keep checking pause flag, but do not update.
            for num, body in enumerate(bodies):
                temp_body = calculate_resultant_force(bodies, body, dt)
                bodies[num] = temp_body
                x = positionData[num][0]
                x.append(temp_body.position.get()[0])
                y = positionData[num][1]
                y.append(temp_body.position.get()[1])
                positionData[num] = [x, y]

# == == ==
# DATA OUTPUT
# == == ==
def statsUpdate(stats):
    '''
    On click of an update button in the stats pane of the GUI, the current position and velocity are inserted into their
    respective fields in the correct stats card, for the user to see.
    '''
    global main
    for num, body in enumerate(main.Bodies):  # Loop through the bodies.
        if main.stats_widgets.index(stats) == num:  # If the stats widget being updated is in the same position as body.
            main.stats_widgets[num].posX.setText(str(body.position.get()[0]))  # Update posX
            main.stats_widgets[num].posY.setText(str(body.position.get()[1]))  # Update posY
            main.stats_widgets[num].velX.setText(str(body.velocity.get()[0]))  # Update velX
            main.stats_widgets[num].velY.setText(str(body.velocity.get()[1]))  # Update velY
            break

'''
The above functions are used to output, and far more importantly, generate data.
-   The statsUpdate() function updates the fields of the correct widget with the correct information by comparing the
    list of bodies with the list of stats widgets. All widget lists match one to one with the list of bodies,
    allowing this technique to work effectively.
-   The generate() function is the core of the simulation despite its apparent simplicity. It uses two flags to control
    when it generates data. data_gen_pause stops the generation temporarily when paused, as the stop flag still == 1.
    data_gen_stop stops the generation completely as the simulation as been terminated. The flags are variables in the
    shared memory created using the multiprocessing module - generate() executes in a separate process to the GUI
    and simulation. To generate positions, the function iterates through the list of bodies, and calculates the resultant
    force the body is experiences converts this to acceleration -> velocity -> position, storing the new updated form of
    the body in the temp_body variable. The positions from this body are accessed using the position object's interface
    (position.get()) and appended to the correct indices of the positionData array. The plotting function reads from this
    array to display the objects on the screen.
'''

# == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == ==
# MAIN SIMULATION CLASS (Handles GUI elements and plotting)
# == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == ==

class Main(QMainWindow, Ui_MainWindow):  # Inherits from QMainWindow and Ui_MainWindow to setup GUI.

    # == == == == == == == == == == == == == == == == == == == == == == == == == ==
    # INIT FUNCTION
    # == == == == == == == == == == == == == == == == == == == == == == == == == ==
    def __init__(self, ):
        super(Main, self).__init__()
        self.setupUi(self) # Creates GUI
        self.config_widgets = []  # List of config widget objects
        self.stats_widgets = []  # List of stats widget objects
        # -/+ floats with exponents of -/+ integer powers
        self.input_mask = re.compile(
            '^[-+]?[0-9]*[.]?[0-9]+([eE]?[-+]?[0-9]+)?$')  # Regex pattern for input validation.

        # Playback
        self.data_gen_process = None  # Variable to store the process object for the generation function.
        self.data_gen_pause = Value('i', 1)  # Pause flag. 1 = PLAY 0 = PAUSE; Used in generate() to prevent update.
        self.data_gen_stop = Value('i', 1)  # Stop flag. 1 = PLAY 0 = STOP; Used in generate() to stay in function
        self.playback_mode = False  # Play = True, Pause = False; Used to change state of play button

        # Animation
        self.fig = None  # Figure
        self.ax1 = None  # Axis
        self.positionData = []  # Stores all positions of bodies.
        self.userBodies = []  # Stores user configured bodies from GUI
        self.expiry = 30000  # Length of orbit to display
        self.pointers = [0 - self.expiry, 0]  # Plotting Pointers
        self.dt = cValue(c_double, 1e3) # Time Multiplier

        # Setup Buttons
        self.create_new_body.clicked.connect(self.add_config)  # Connect create new body button
        self.import_body.clicked.connect(lambda: self.add_import_config(self.returnSelectedItems()))  # Connect create new body button
        self.play_button.clicked.connect(self.play)  # Connect play button
        self.stop_button.clicked.connect(self.stop)  # Connect stop button

        # Setup console box
        self.textEdit = QTextEdit()  # Create text edit widget for console
        self.console_box.setWidget(self.textEdit)  # Add the widget to the console box scroll area
        self.setUpDB() # Create table widget for library pane.

    # == == == == == == == == == == == == == == == == == == == == == == == == == ==
    #  BODY LIBRARY WIDGET
    # == == == == == == == == == == == == == == == == == == == == == == == == == ==

    # == == ==
    # CREATE/UPDATE/SORT LIBRARY WIDGET
    # == == ==
    def setUpDB(self):
        '''
        Creates and updates body library table in library pane.
        '''
        self.model = QStandardItemModel() # Create GUI table widget.
        self.model.setColumnCount(5) # Define widget to have 5 columns
        headerNames = ["Name", "Mass", "Pos", "Vel", "Type"]
        self.model.setHorizontalHeaderLabels(headerNames) # Set header names
        self.body_data = readFromDatabase() # Read data
        for item in self.body_data:
            row = []
            for element in item:
                cell = QStandardItem(element)
                cell.setEditable(False)
                row.append(cell)
            self.model.appendRow(row)
        self.tableView.setModel(self.model) # Assign data to table
        #self.sort.connect(mergeSort(self.model))

    # == == ==
    # RETURN SELECTED RECORDS
    # == == ==
    def returnSelectedItems(self):
        '''
        Returns the data for the bodies that are selected in the table in library pane.
        '''
        return sorted(set(index.row() for index in self.tableView.selectedIndexes()))

    # == == == == == == == == == == == == == == == == == == == == == == == == == ==
    # PLAYBACK CONTROL
    # == == == == == == == == == == == == == == == == == == == == == == == == == ==

    # == == ==
    # PLAY
    # == == ==
    def play(self):
        if self.userBodies == []:  # If there is nothing configured, end play function here.
            main.log("No bodies configured.")  # Log to console.
            return  # End play function, do not animate.

        if not self.input_mask.match(self.time.text()): # If the time step entered is invalid, end play function.
            main.log(changeTextColour("Invalid time entered.", RED)) # Log error to console
            return # End play function

        self.dt = cValue(c_double, float(self.time.text())) # Set time step to value in field. Shared memory value

        if self.data_gen_process == None:  # If there is no generate process started already...
            self.play_button.setEnabled(False)  # Disable play_button to prevent double clicks.
            self.body_config_scrollArea.setEnabled(False)  # Disable the config area
            self.create_new_body.setEnabled(False)  # Disable the create_new_body button

            bodies = [body[0] for body in self.userBodies]  # Bodies to be simulated.
            for num, body in enumerate(bodies):
                bodies[num].id = num  # Assign unique id to all bodies being simulated
            manager = Manager()  # Shared multidimensional array manager accessible by both processes.
            bodyManager = Manager()
            self.Bodies = bodyManager.list()  # Shared memory array for body list. Required by statsUpdate!
            self.positionData = manager.list()  # Shared multidimensional array for positionData

            self.data_gen_pause = Value('i', 1)  # Reset pause and stop flags, otherwise animation will NOT reset!
            self.data_gen_pause.value = 1
            self.data_gen_stop = Value('i', 1)
            self.data_gen_stop.value = 1

            for body in bodies:  # Initialise positionData and Bodies
                self.positionData.append([[], []])  # Creates x y lists for each body in the body list.
                self.Bodies.append(body)

            self.data_gen_process = Process(target=generate, args=(self.Bodies,
                                                                   self.positionData,
                                                                   self.data_gen_pause,
                                                                   self.data_gen_stop,
                                                                   self.dt,))  # Create process object.
            # Must have trailing comma after final argument (self.dt)

            self.data_gen_process.start()  # Spawn new process.
            main.log("Data gen process started: {}".format(self.data_gen_process.pid))  # Log to console
            for num, body in enumerate(self.Bodies):  # Initialise the stats widgets.
                self.stats_widgets[num].name.setText(body.name)
                self.stats_widgets[num].mass.setText(str(body.mass))
                self.stats_widgets[num].setEnabled(True)
            self.play_button.setEnabled(True)  # Re-enable play button.

        self.playback_mode = not self.playback_mode  # Toggle playback_mode flag.
        if self.playback_mode:  # If in PLAY mode.
            self.play_button.setText("Pause")  # Set text of play button to PAUSE
            main.log("Simulation Played!")  # Log to console
            self.data_gen_pause.value = 1  # Set pause flag to PLAY (1)
            self.playback_mode = True  # Set playback_mode to TRUE (PLAY)
            if self.data_gen_process is not None:
                self.ani.event_source.start()  # If played after pause, restart animation

        else:  # If in PAUSE mode.
            self.play_button.setText("Play")  # Set text of play button to PLAY
            self.pause()  # Start PAUSE function.
            self.playback_mode = False  # Set playback_mode flag to PAUSE (False)

    '''
    The above function is the critical to the smooth execution of the simulation. It first checks the prerequisites
    required for the simulation - saved bodies to be simulated and a valid time step. If those two conditions are not
    met then the play function will terminate and log messages to console explaining why. Once the prerequisites are
    met then it checks if a data generation process already exists and if not, it starts to commence the simulation.

    First, it disables the GUI elements that the user is disallowed to interact with during play mode. Next, it collects
    all the saved body data that the user wants to simulate into one array. After that it creates a set of special
    variables that can be accessed by different processes running simultaneously. Normal python variables CANNOT be
    accessed from outside the python process they were initialised in. The variables that need to be accessed by
    more than one process are the pause and play flags, list of bodies and time step. Next, the function sets up
    a process object for the data generation process that needs to fun in parallel with the animation. It passes
    the shared memory variables that it just initialised to the generate function too. Finally, it spawns a new data
    generation process and logs a message to the console.  At this point in the program, the play function and the data
    generation function (generate()) are executing simultaneously.

    It toggles the playback_mode flag as the play button was clicked. If the simulation is play mode, it makes the necessary
    changes to the GUI and starts the animation (restarts if it was played after pause). If the simulation is in pause mode,
    then the pause method is called and the playback_mode is set to false.
    '''

    # == == ==
    # STOP PLAYBACK
    # == == ==
    def stop(self):
        '''
        Stops the simulation by ending data_gen processes and terminating animation playback.
        '''
        self.data_gen_stop.value = 0  # Stop the data generation in the generate function.
        if self.data_gen_process is not None:  # If there is a process to be stopped...
            pid = self.data_gen_process.pid  # Save pid of process for the console output.
            self.data_gen_process.join()  # Stop the process
            self.data_gen_process = None  # Set process attribute to None
            main.log("Data gen process stopped: {}".format(pid))  # Log to console
            self.playback_mode = False  # Reset playback_mode flag for next play()
            self.ani.event_source.stop()  # Stop animation

            # Enable all GUI elements that were disabled during simulation
            self.body_config_scrollArea.setEnabled(True)
            self.create_new_body.setEnabled(True)
            self.play_button.setText("Play")

            self.ax1.clear()  # Clear the axes

    # == == ==
    # PAUSE PLAYBACK
    # == == ==
    def pause(self):
        '''
        Pauses the simulation by toggling data_gen_pause flag, stopping animation and logging to console.
        '''
        self.ani.event_source.stop()  # Stop animation.
        self.data_gen_pause.value = 0
        # Stop further data generation by changing pause flag, to ensure statsUpdate() only updates to latest
        # plotted values.
        main.log("Simulation Paused!")  # Log to console.

    # == == == == == == == == == == == == == == == == == == == == == == == == == ==
    # BODY CONFIGURATION
    # == == == == == == == == == == == == == == == == == == == == == == == == == ==

    def SaveBody(self, widget, name, mass, position, velocity, type):
        '''
        Gathers data from the fields of the widget on which the 'Save Body' button was clicked, and instantiates Body
        objects with the data gathered. If 'Save Body' is clicked more than once, the correct body object is updated with
        new details.
        '''
        invalid = False  # Initialise validity flag to False
        if name == "":  # Presence check for name first.
            main.log(changeTextColour("Enter a name!".format(name), RED))
            return
        if not self.input_mask.match(mass):  # Validates mass
            main.log(changeTextColour("Invalid input for mass of {}".format(name), RED))  # Use changeTextColour.
            invalid = True
        if not self.input_mask.match(position[0]):  # Validates x position
            main.log(changeTextColour("Invalid input for x position of {}".format(name), RED))  # Log results.
            invalid = True
        if not self.input_mask.match(position[1]):  # Validates y position
            main.log(changeTextColour("Invalid input for y position of {}".format(name), RED))
            invalid = True
        if not self.input_mask.match(velocity[0]):  # Validates x velocity
            main.log(changeTextColour("Invalid input for x velocity of {}".format(name), RED))
            invalid = True
        if not self.input_mask.match(velocity[1]):  # Validates y velocity
            main.log(changeTextColour("Invalid input for y velocity of {}".format(name), RED))
            invalid = True
        if invalid:
            main.log("-" * 30)
            return  # Stop save function if anything is invalid.

        # If all is valid and the body is being SAVED not created...
        for body in self.userBodies:  # Iterate through userBodies to find corresponding body object to widget.
            if body[1] == widget:
                body[0].name = name
                body[0].mass = float(mass)
                body[0].position.set(float(position[0]), float(position[1]))
                body[0].velocity.set(float(velocity[0]), float(velocity[1]))
                body[0].type = str(type)
                main.log("{} Saved.".format(body[0].name))  # Log to console
                return  # End function

        # If a new body is being created (because the function was not ended earlier)
        newBody = Body()
        newBody.name = name
        newBody.mass = float(mass)  # Convert validated inputs to floats
        newBody.position.set(float(position[0]), float(position[1]))
        newBody.velocity.set(float(velocity[0]), float(velocity[1]))
        newBody.type = str(type)
        self.userBodies.append((newBody, widget))  # Append to userBodies
        main.log("{} created!".format(newBody.name))  # Log to console
        main.log(str(newBody))  # Log details to console

    # == == == == == == == == == == == == == == == == == == == == == == == == == ==
    # ANIMATION
    # == == == == == == == == == == == == == == == == == == == == == == == == == ==

    def addMpl(self):
        '''
        Adds the matplotlib figure in the correct layout of the GUI. Adds the toolbar to the same layout.
        '''
        self.fig = Figure()  # Create figure.
        self.ax1 = self.fig.add_subplot(1, 1, 1)  # Create axis from subplot
        self.ax1.axis('equal')  # Stop distortion of orbits, by making each axis graduations same width in pixels.
        self.ax1.autoscale(False)
        self.canvas = FigureCanvas(self.fig)  # Create canvas for figure.
        self.fig.set_facecolor('white')  # Set background
        self.mplvl.addWidget(self.canvas)  # Add canvas as widget to mplvl layout in window.ui file.
        self.canvas.draw()  # Draw canvas
        logging.info("Added Matplotlib graph.")

        # Setup toolbar
        self.toolbar = NavigationToolbar(self.canvas, self.mplwindow, coordinates=True)  # Instantiate toolbar.
        self.toolbar_container.addWidget(self.toolbar)  # Add toolbar to layout.
        logging.info("Added toolbar")

    def animate(self, i):
        '''
        Reads positionData array and front and back pointers to plot the relevant parts of the orbit. Increasing the
        'Plot Speed' of the simulation using the slider increases the amount by which the front pointer increases each
        frame of the animation.
        '''
        self.ax1.clear()
        self.ax1.autoscale(self.autoscale.isChecked()) # Set 'autoscale' attribute to value of checkbox.
        for body in self.positionData:  # Loop through each body's position array in positionData (shared memory!)
            back = max(0, self.pointers[0])  # Set back2 to 0 if negative.
            front = max(0, self.pointers[1])
            self.pointers[1] = front
            self.ax1.plot(body[0][back:front],  # x values of current body being plotted.
                          body[1][back:front],  # y values '' ''
                          marker='o',  # Marker used to denote current position of body
                          markevery=[-1])  # Position of marker on the line (second last)
        self.pointers[1] += self.simspeed.value()  # increase/decrease front pointer by sim speed.
        self.pointers[0] = self.pointers[1] - self.expiry  # reset back pointer

    # == == == == == == == == == == == == == == == == == == == == == == == == == ==
    # WIDGETS DYNAMICALLY GENERATED BY THE USER
    # == == == == == == == == == == == == == == == == == == == == == == == == == ==

    # == == ==
    # IMPORTED BODY CONFIGURATION
    # == == ==
    def add_import_config(self, selected_indices):
        '''
        Creates configuration card(s) in the leftmost pane with the imported data already filed in the
        correct fields.
        '''
        data = []
        for pos, row in enumerate(selected_indices):
            data.append([])
            for column in range(self.model.columnCount()):
                index = self.model.index(row, column)
                data[pos].append(str(self.model.data(index)))

        for body in data:
            position = body[2].split(',')
            position = [part.split('\'')[1] for part in position]
            velocity = body[3].split(',')
            velocity = [part.split('\'')[1] for part in velocity]
            self.add_config(data = [body[0],
                                    body[1],
                                    position[0],
                                    position[1],
                                    velocity[0],
                                    velocity[1],
                                    body[4]])
    # == == ==
    # NEW BODY CONFIGURATION
    # == == ==
    @pyqtSlot()
    def add_config(self, data = None):
        '''
        Creates a blank configuration card in the left most pane. Connects all the buttons in the card to
        correct functions.
        '''
        config = BodyConfig()  # Create config widget
        if data is not None:
            config.name.setText(data[0])
            config.mass.setText(data[1])
            config.posX.setText(data[2])
            config.posY.setText(data[3])
            config.velX.setText(data[4])
            config.velY.setText(data[5])
            index = config.type.findText(data[6], Qt.MatchFixedString)
            if index >= 0:
                config.type.setCurrentIndex(index)

        stats = BodyStats()  # Create stats widget in the other pane
        stats.setEnabled(False)  # Disable the stats widget
        config.delete_btn.clicked.connect(lambda: self.del_config(config, stats))  # Connect delete button on config.
        config.save.clicked.connect(lambda: self.SaveBody(config,
                                                          config.name.text(),
                                                          config.mass.text(),
                                                          (config.posX.text(), config.posY.text()),
                                                          (config.velX.text(), config.velY.text()),
                                                          config.type.currentText())) # Connect save button to function

        config.db_save.clicked.connect(lambda: saveToDatabase(config.name.text(),
                                                              config.mass.text(),
                                                              (config.posX.text(), config.posY.text()),
                                                              (config.velX.text(), config.velY.text()),
                                                              config.type.currentText(), self)) # Connect save to db function

        stats.update.clicked.connect(lambda: statsUpdate(stats))  # Connect update button on stats widget
        self.config_widgets.append(config)  # Append widgets to respective arrays.
        self.stats_widgets.append(stats)
        self.bodyConfig.addWidget(self.config_widgets[-1])  # Add to scroll areas respectively.
        self.stats.addWidget(self.stats_widgets[-1])

    # == == ==
    # DELETE BODY CONFIGURATION
    # == == ==
    @pyqtSlot()
    def del_config(self, widget, stats_widget):
        '''
        Deletes a widget from the leftmost pane and deletes its respective statistics widget from the middle pane.
        '''
        self.bodyConfig.removeWidget(widget)  # Remove from scroll areas.
        self.stats.removeWidget(stats_widget)
        stats_widget.deleteLater()  # (This is just required, don't know why)
        widget.deleteLater()
        for num, body in enumerate(self.userBodies):
            if body[1] == widget:
                del self.userBodies[num]  # Delete config object from the userBodies array
                break

        for num, widg in enumerate(self.stats_widgets):
            if widg == stats_widget:
                del self.stats_widgets[num]  # Delete stats object from stats_wdigets array
                break

        main.log("Widget removed.")  # Log to console
        widget = None  # (This is just required, don't know why)
        stats_widget = None

    # == == == == == == == == == == == == == == == == == == == == == == == == == ==
    # LOG TO CONSOLE
    # == == == == == == == == == == == == == == == == == == == == == == == == == ==

    def log(self, text):
        '''
        Logs text to the console box in bottom left.
        '''
        self.textEdit.append(text)
        logging.debug(text)

# == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == ==
# INSTANTIATION SEQUENCE
# == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == ==
if __name__ == "__main__":
    app = QApplication(sys.argv)  # Initialise application
    main = Main()  # Instantiate main object
    main.addMpl()  # Add matplotlib!
    # main.showMaximized() #Show GUI maximised
    main.ani = animation.FuncAnimation(main.fig, main.animate)  # Create animation updating every 2ms.
    # Must be OUTSIDE class otherwise the animation will not function.
    main.show()  # Show GUI
    sys.exit(app.exec_())  # Exit function if app closed.
