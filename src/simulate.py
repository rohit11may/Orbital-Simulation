# Orbital Simulation Practical Project
# Rohit Prasad
# 2016-2017
# Last changed on 11/12/2016

# Imports
# GUI Libraries.
from PyQt4.QtGui import *
from PyQt4.QtCore import Qt
from PyQt4.QtCore import pyqtSlot
from PyQt4.uic import loadUiType
from matplotlib.backends.backend_qt4agg import (
    FigureCanvasQTAgg as FigureCanvas,
    NavigationToolbar2QT as NavigationToolbar)

# Multiprocessing and GUI Threading module.
from multiprocessing import Process, Manager, Value
from multiprocessing.sharedctypes import Value as cValue
from ctypes import c_double

# Matplotlib
import matplotlib.animation as animation
from matplotlib.figure import Figure

# Local
from src.body import Body
from src.orbitmath import calculate_resultant_force

# Others
import sys
import logging
import re

AU = 149598e6
RED = '#ff0000'
BLUE = '#0000ff'
GREEN = '#00ff00'

logging.basicConfig(format='%(asctime)s.%(msecs)03d // %(message)s',
                    filename="..//logs//logfile.log",
                    datefmt='%H:%M:%S',
                    filemode='w',
                    level=logging.DEBUG)

Ui_MainWindow, QMainWindow = loadUiType('..//GUI//window.ui')  # Load UI file from GUI folder.
UI_BodyConfigMainWindow, BodyConfigMainWindow = loadUiType(
    '..//GUI//body_config_widget.ui')  # Load config UI file from GUI folder.
UI_BodyStatsMainWindow, BodyStatsMainWindow = loadUiType(
    '..//GUI//body_stats_widget.ui')  # Load stats widget UI file from GUI folder.


def changeTextColour(text, colour):
    new_text = "<span style=\" color:{};\" >".format(colour)
    new_text += text
    new_text += "</span>"
    return new_text


class BodyConfig(BodyConfigMainWindow, UI_BodyConfigMainWindow):  # Setup config UI for use in GUI
    def __init__(self):
        super(BodyConfig, self).__init__()
        self.setupUi(self)


class BodyStats(BodyStatsMainWindow, UI_BodyStatsMainWindow):  # Setup stats UI for use in GUI
    def __init__(self):
        super(BodyStats, self).__init__()
        self.setupUi(self)

def saveToDatabase(name, mass, position, velocity, type):
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
    return "Body Saved to DB!" # return log message

def deleteFromDatabase(name):
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

def readFromDatabase():
    db_read = open("..//lib//body_db.db", 'r')  # Open file in read mode to check for duplicates
    data = []
    for line in db_read.readlines():
        datum = line.rstrip().split(';')
        data.append(datum)
    return data

def generate(bodies, positionData, data_gen_pause, data_gen_stop, dt):
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


def statsUpdate(stats):
    global main
    for num, body in enumerate(main.Bodies):  # Loop through the bodies.
        if main.stats_widgets.index(stats) == num:  # If the stats widget being updated is in the same position as body.
            main.stats_widgets[num].posX.setText(str(body.position.get()[0]))  # Update posX
            main.stats_widgets[num].posY.setText(str(body.position.get()[1]))  # Update posY
            main.stats_widgets[num].velX.setText(str(body.velocity.get()[0]))  # Update velX
            main.stats_widgets[num].velY.setText(str(body.velocity.get()[1]))  # Update velY
            break


class Main(QMainWindow, Ui_MainWindow):  # Go to Form -> View Code in QTDesigner to see structure of GUI.
    def __init__(self, ):
        super(Main, self).__init__()
        self.setupUi(self)
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
        self.dt = cValue(c_double, 1e3)

        # Setup Buttons
        self.create_new_body.clicked.connect(self.add_config)  # Connect create new body button
        self.import_body.clicked.connect(lambda: self.add_import_config(self.returnSelectedItems()))  # Connect create new body button
        self.play_button.clicked.connect(self.play)  # Connect play button
        self.stop_button.clicked.connect(self.stop)  # Connect stop button

        # Setup console box
        self.textEdit = QTextEdit()  # Create text edit widget for console
        self.console_box.setWidget(self.textEdit)  # Add the widget to the console box scroll area

        # Body library
        self.model = QStandardItemModel()
        self.model.setColumnCount(5)
        headerNames = ["Name", "Mass", "Pos", "Vel", "Type"]
        self.model.setHorizontalHeaderLabels(headerNames)
        self.body_data = readFromDatabase()
        for item in self.body_data:
            row = []
            for element in item:
                cell = QStandardItem(element)
                cell.setEditable(False)
                row.append(cell)
            self.model.appendRow(row)
        self.tableView.setModel(self.model)



    # STOP BUTTON FUNCTION
    def stop(self):
        self.data_gen_stop.value = 0  # Stop the data generation in the generate function.
        if self.data_gen_process is not None:  # If there is a process to be stopped...
            pid = self.data_gen_process.pid  # Save pid of process for the console output.
            self.data_gen_process.join()  # Stop the process
            self.data_gen_process = None  # Set process attribute to None
            main.log("Data gen process stopped: {}".format(pid))  # Log to console
            self.playback_mode = False  # Reset playback_mode flag for next play()
            self.ani.event_source.stop()  # Stop animation

            # Enable all GUI elements
            self.body_config_scrollArea.setEnabled(True)
            self.create_new_body.setEnabled(True)
            self.play_button.setText("Play")

            self.ax1.clear()  # Try and clear the screen?

    # PAUSE BUTTON FUNCTION
    def pause(self):
        self.ani.event_source.stop()  # Stop animation.
        self.data_gen_pause.value = 0
        # Stop further data generation by changing pause flag, to ensure statsUpdate() only updates to latest
        # plotted values.
        main.log("Simulation Paused!")  # Log to console.

    def SaveBody(self, widget, name, mass, position, velocity, type):
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
        for body in self.userBodies:  # Iterate through userbodies to find corresponding body object to widget.
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

    def animate(self, i):
        self.ax1.clear()
        self.ax1.autoscale(self.autoscale.isChecked())
        for body in self.positionData:  # Loop through each body's position array in positionData (shared memory!)
            back = max(0, self.pointers[0])  # Set back2 to 0 if negative.
            front = max(0, self.pointers[1])
            self.pointers[1] = front
            self.ax1.plot(body[0][back:front],  # x values of current body being plotted.
                          body[1][back:front],  # y values '' ''
                          marker='o',  # Marker used to denote current position
                          markevery=[-1])  # Position of marker (second last)
        self.pointers[1] += self.simspeed.value()  # increase/decrease front pointer by sim speed.
        self.pointers[0] = self.pointers[1] - self.expiry  # reset back pointer

    def play(self):
        if self.userBodies == []:  # If there is nothing configured, end play function here.
            main.log("No bodies configured.")  # Log to console.
            return  # End play function, do not animate.

        if not self.input_mask.match(self.time.text()):
            main.log(changeTextColour("Invalid time entered.", RED))
            return

        self.dt = cValue(c_double, float(self.time.text()))

        if self.data_gen_process == None:  # If there is no generate process started already...
            self.play_button.setEnabled(False)  # Disable play_button to prevent double clicks.
            self.body_config_scrollArea.setEnabled(False)  # Disable the config area
            self.create_new_body.setEnabled(False)  # Disable the create_new_body button

            bodies = [body[0] for body in self.userBodies]  # Bodies to be simulated.
            for num, body in enumerate(bodies):
                bodies[num].id = num  # Assign unique id to all bodies being simulated
            manager = Manager()  # Shared multidimensional array manager accessible by both processes.
            bodyManager = Manager()
            self.Bodies = bodyManager.list()  # Shared memory array for body list. Required by statsUpdate!.
            self.positionData = manager.list()  # Shared multidimensional array

            self.data_gen_pause = Value('i', 1)  # Reset pause and stop flags, otherwise animation will NOT reset!
            self.data_gen_pause.value = 1
            self.data_gen_stop = Value('i', 1)
            self.data_gen_stop.value = 1

            for body in bodies:  # Initialise positionData and Bodies
                self.positionData.append([[], []])  # Creates x y lists for each body in the body list.
                self.Bodies.append(body)
                # for bodyA in bodies:
                #     if bodyA.id != body.id:
                #         maxDistance.append(distance(bodyA, body).getMagnitude())
            # maxDistance = max(maxDistance)
            # main.log("Maximum distance = {}".format(str(maxDistance)))

            self.data_gen_process = Process(target=generate, args=(self.Bodies,
                                                                   self.positionData,
                                                                   self.data_gen_pause,
                                                                   self.data_gen_stop,
                                                                   self.dt,))  # Create process object.

            # Must have trailing comma after final argument.
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

    def addMpl(self):
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

    def log(self, text):
        self.textEdit.append(text)
        logging.debug(text)

    def returnSelectedItems(self):
        return sorted(set(index.row() for index in self.tableView.selectedIndexes()))

    def add_import_config(self, selected_indices):
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
    @pyqtSlot()
    def add_config(self, data = None):
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

        stats = BodyStats()  # Create stats widget
        stats.setEnabled(False)  # Disable the stats widget
        config.delete_btn.clicked.connect(lambda: self.del_config(config, stats))  # Connect delete button on config.
        config.save.clicked.connect(lambda: self.SaveBody(config,
                                                          config.name.text(),
                                                          config.mass.text(),
                                                          (config.posX.text(), config.posY.text()),
                                                          (config.velX.text(), config.velY.text()),
                                                          config.type.currentText()))  # Connect save button.

        config.db_save.clicked.connect(lambda: saveToDatabase(config.name.text(),
                                                              config.mass.text(),
                                                              (config.posX.text(), config.posY.text()),
                                                              (config.velX.text(), config.velY.text()),
                                                              config.type.currentText()))

        stats.update.clicked.connect(lambda: statsUpdate(stats))  # Connect update button
        self.config_widgets.append(config)  # Append widgets to respective arrays.
        self.stats_widgets.append(stats)

        self.bodyConfig.addWidget(self.config_widgets[-1])  # Add to scroll areas respectively.
        self.stats.addWidget(self.stats_widgets[-1])

    @pyqtSlot()
    def del_config(self, widget, stats_widget):
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


if __name__ == "__main__":
    app = QApplication(sys.argv)  # Initialise application
    main = Main()  # Instantiate main object
    main.addMpl()  # Add matplotlib!
    # main.showMaximized() #Show GUI maximised
    main.ani = animation.FuncAnimation(main.fig, main.animate)  # Create animation updating every 2ms.
    # Must be OUTSIDE class otherwise the animation will not function. Something to do with object being collected
    # for garbage (expiring because its local or something)
    main.show()  # Show GUI
    sys.exit(app.exec_())  # Exit function
