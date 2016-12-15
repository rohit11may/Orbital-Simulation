# Orbital Simulation Practical Project
# Rohit Prasad
# 2016-2017
# Last changed on 11/12/2016

# Imports
# GUI Libraries.
from PyQt4.QtGui import *
from PyQt4.QtCore import pyqtSlot
from PyQt4.uic import loadUiType
from matplotlib.backends.backend_qt4agg import (
    FigureCanvasQTAgg as FigureCanvas,
    NavigationToolbar2QT as NavigationToolbar)

# Multiprocessing module.
from multiprocessing import Process, Manager

# Matplotlib
import matplotlib.animation as animation
from matplotlib.figure import Figure

# Local
from src.body import Body
from src.orbitmath import calculate_resultant_force
from src.vector import Vector
import src.real_body_config as lib

# Others
import sys
import logging
import re
from random import randint

AU = 149598e6
RED = '#ff0000'
BLUE = '#0000ff'
GREEN = '#00ff00'

userBodies = []
positionData = []
pointers = []
# -/+ floats with exponents of -/+ integer powers
input_mask = re.compile('^[-+]?[0-9]*[.]?[0-9]+([eE]?[-+]?[0-9]+)?$')

logging.basicConfig(format='%(asctime)s.%(msecs)03d // %(message)s',
                    filename="..//logs//logfile.log",
                    datefmt='%H:%M:%S',
                    filemode='w',
                    level=logging.DEBUG)

Ui_MainWindow, QMainWindow = loadUiType('..//GUI//window.ui')  # Load UI file from GUI folder.
UI_BodyConfigMainWindow, BodyConfigMainWindow = loadUiType(
    '..//GUI//body_config_widget.ui')  # Load UI file from GUI folder.


def generate(bodies, positionData):
    while True:
        for num, body in enumerate(bodies):
            temp_body = calculate_resultant_force(bodies, body)
            bodies[num] = temp_body
            x = positionData[num][0]
            x.append(temp_body.position.get()[0])
            y = positionData[num][1]
            y.append(temp_body.position.get()[1])
            positionData[num] = [x, y]


def changeTextColour(text, colour):
    new_text = "<span style=\" color:{};\" >".format(colour)
    new_text += text
    new_text += "</span>"
    return new_text


def SaveBody(widget, name, mass, position, velocity, type):
    global userBodies, input_mask, RED
    invalid = False
    if name == "":  # Presence check for name.
        main.log(changeTextColour("Enter a name!".format(name), RED));
        return
    if not input_mask.match(mass):  # Validates mass
        main.log(changeTextColour("Invalid input for mass of {}".format(name), RED))
        invalid = True
    if not input_mask.match(position[0]):  # Validates x position
        main.log(changeTextColour("Invalid input for x position of {}".format(name), RED))
        invalid = True
    if not input_mask.match(position[1]):  # Validates y position
        main.log(changeTextColour("Invalid input for y position of {}".format(name), RED))
        invalid = True
    if not input_mask.match(velocity[0]):  # Validates x velocity
        main.log(changeTextColour("Invalid input for x velocity of {}".format(name), RED))
        invalid = True
    if not input_mask.match(velocity[1]):  # Validates y velocity
        main.log(changeTextColour("Invalid input for y velocity of {}".format(name), RED))
        invalid = True
    if invalid: main.log("-" * 30); return

    for body in userBodies:
        if body[1] == widget:
            body[0].name = name
            body[0].mass = float(mass)
            body[0].position.set(float(position[0]), float(position[1]))
            body[0].velocity.set(float(velocity[0]), float(velocity[1]))
            body[0].type = str(type)
            main.log("{} Saved.".format(body[0].name))
            return

    newBody = Body()
    newBody.name = name
    newBody.mass = float(mass)
    newBody.position.set(float(position[0]), float(position[1]))
    newBody.velocity.set(float(velocity[0]), float(velocity[1]))
    newBody.type = str(type)
    userBodies.append((newBody, widget))
    main.log("{} created!".format(newBody.name))
    main.log(str(userBodies))


class BodyConfig(BodyConfigMainWindow, UI_BodyConfigMainWindow):
    def __init__(self):
        super(BodyConfig, self).__init__()
        self.setupUi(self)


class Main(QMainWindow, Ui_MainWindow):  # Go to Form -> View Code in QTDesigner to see structure of GUI.
    def __init__(self, ):
        super(Main, self).__init__()
        self.setupUi(self)
        self.config_widgets = []

        # Setup Buttons
        self.create_new_body.clicked.connect(self.add_config)
        self.play_button.clicked.connect(self.play)

        # Setup console box
        self.textEdit = QTextEdit()
        self.console_box.setWidget(self.textEdit)
        logging.info("Setup Console Box")

    def addMpl(self, fig):
        self.canvas = FigureCanvas(fig)  # Create canvas for figure.
        fig.set_facecolor('white')
        self.mplvl.addWidget(self.canvas)  # Add canvas as widget to mplvl layout in window.ui file.
        self.canvas.draw()  # Draw canvas
        logging.info("Added Matplotlib graph.")

    def addToolBar(self):
        # Setup toolbar
        self.toolbar = NavigationToolbar(self.canvas, self.mplwindow, coordinates=True)  # Instantiate toolbar.
        self.toolbar_container.addWidget(self.toolbar)  # Add toolbar to layout.
        logging.info("Added toolbar")

    def log(self, text):
        self.textEdit.append(text)
        logging.debug(text)

    @pyqtSlot()
    def add_config(self):
        config = BodyConfig()
        config.delete_btn.clicked.connect(lambda: self.del_config(config))
        config.save.clicked.connect(lambda: SaveBody(config,
                                                     config.name.text(),
                                                     config.mass.text(),
                                                     (config.posX.text(), config.posY.text()),
                                                     (config.velX.text(), config.velY.text()),
                                                     config.type.currentText()))

        self.config_widgets.append(config)
        self.bodyConfig.addWidget(self.config_widgets[-1])

    @pyqtSlot()
    def del_config(self, widget):
        global userBodies
        self.bodyConfig.removeWidget(widget)
        widget.deleteLater()
        for num, body in enumerate(userBodies):
            if body[1] == widget:
                del userBodies[num]
                break
        main.log(str(widget) + " removed.")
        widget = None
        main.log(str(userBodies))

    def animate(i):
        global positionData, pointers, expiry
        print("HERE")
        ax1.clear()  # clear lines
        for body in positionData:
            back2 = max(0, pointers[0])  # Set back2 to 0 if negative.
            ax1.plot(body[0][back2::],  # x values of current body being plotted.
                     body[1][back2::],  # y values '' ''
                     marker='o',  # Marker used to denote current position
                     markevery=[-1])  # Position of marker (second last)

        pointers[1] += 100  # increment front pointer
        pointers[0] = pointers[1] - expiry  # reset back pointer

    def play(self):

        global positionData, pointers, fig, ax1
        if userBodies == []:
            main.log("No bodies configured.")
            return
        bodies = [body[0] for body in userBodies]  # Bodies to be simulated.
        print(bodies)
        for num, body in enumerate(bodies):
            bodies[num].id = num  # Assign unique id to all bodies being simulated

        manager = Manager()  # Shared multidimensional array manager accessible by both processes.
        positionData = manager.list()  # Shared multidimensional array
        for body in bodies:
            positionData.append([[], []])  # Creates x y lists for each body in the body list.

        p = Process(target=generate, args=(bodies, positionData,))  # Creates process p for data generation
        # Must have trailing comma after final argument.
        expiry = 3000000
        pointers = [0 - expiry, 0]  # Plotting Pointers
        p.start()  # Spawn new process.
        ani = animation.FuncAnimation(fig, self.animate)  # Create animation updating every 2ms.


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main = Main()

    fig = Figure()
    ax1 = fig.add_subplot(1, 1, 1)
    ax1.axis('equal')

    main.addMpl(fig)  # Add figure to the GUI
    main.addToolBar()  # Add toolbar to the GUI; MUST BE CALLED AFTER .addMpl()
    # main.showMaximized() #Show GUI
    main.show()
    sys.exit(app.exec_())
