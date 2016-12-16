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
from multiprocessing import Process, Manager, Value

# Matplotlib
import matplotlib.animation as animation
from matplotlib.figure import Figure

# Local
from src.body import Body
from src.orbitmath import calculate_resultant_force
import src.real_body_config as lib

# Others
import sys
import logging
import re

AU = 149598e6
RED = '#ff0000'
BLUE = '#0000ff'
GREEN = '#00ff00'

# -/+ floats with exponents of -/+ integer powers

logging.basicConfig(format='%(asctime)s.%(msecs)03d // %(message)s',
                    filename="..//logs//logfile.log",
                    datefmt='%H:%M:%S',
                    filemode='w',
                    level=logging.DEBUG)

Ui_MainWindow, QMainWindow = loadUiType('..//GUI//window.ui')  # Load UI file from GUI folder.
UI_BodyConfigMainWindow, BodyConfigMainWindow = loadUiType(
    '..//GUI//body_config_widget.ui')  # Load UI file from GUI folder.




def changeTextColour(text, colour):
    new_text = "<span style=\" color:{};\" >".format(colour)
    new_text += text
    new_text += "</span>"
    return new_text





class BodyConfig(BodyConfigMainWindow, UI_BodyConfigMainWindow):
    def __init__(self):
        super(BodyConfig, self).__init__()
        self.setupUi(self)



def generate(bodies, positionData, data_gen):
    while data_gen.value == 1:
        for num, body in enumerate(bodies):
            temp_body = calculate_resultant_force(bodies, body)
            bodies[num] = temp_body
            x = positionData[num][0]
            x.append(temp_body.position.get()[0])
            y = positionData[num][1]
            y.append(temp_body.position.get()[1])
            positionData[num] = [x, y]

class Main(QMainWindow, Ui_MainWindow):  # Go to Form -> View Code in QTDesigner to see structure of GUI.
    def __init__(self, ):
        super(Main, self).__init__()
        self.setupUi(self)
        self.config_widgets = []
        self.input_mask = re.compile('^[-+]?[0-9]*[.]?[0-9]+([eE]?[-+]?[0-9]+)?$')

        self.fig = None
        self.ax1 = None
        self.data_gen_process = None
        self.data_gen = False # True = Data being generated. False = No data generated.
        self.playback_mode = False # Play = True, Pause = False

        # Animation
        self.positionData = []
        self.userBodies = []
        self.expiry = 30000
        self.pointers = [0 - self.expiry, 0]  # Plotting Pointers

        # Setup Buttons
        self.create_new_body.clicked.connect(self.add_config)
        self.play_button.clicked.connect(self.play)
        self.stop_button.clicked.connect(self.stop)

        # Setup console box
        self.textEdit = QTextEdit()
        self.console_box.setWidget(self.textEdit)

        logging.info("Setup Console Box")

    def stop(self):
        self.data_gen.value = 0
        if self.data_gen_process != None:
            pid = self.data_gen_process.pid
            self.data_gen_process.join(); self.data_gen_process = None
            main.log("Data gen process stopped: {}".format(pid))
            self.ax1.clear()
        return

    def pause(self):
        self.ani.event_source.stop()
        main.log("Simulation Paused!")

    def SaveBody(self, widget, name, mass, position, velocity, type):
        invalid = False
        if name == "":  # Presence check for name.
            main.log(changeTextColour("Enter a name!".format(name), RED));
            return
        if not self.input_mask.match(mass):  # Validates mass
            main.log(changeTextColour("Invalid input for mass of {}".format(name), RED))
            invalid = True
        if not self.input_mask.match(position[0]):  # Validates x position
            main.log(changeTextColour("Invalid input for x position of {}".format(name), RED))
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
        if invalid: main.log("-" * 30); return

        for body in self.userBodies:
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
        self.userBodies.append((newBody, widget))
        main.log("{} created!".format(newBody.name))
        main.log(str(self.userBodies))

    def animate(self, i):
        self.ax1.clear()  # clear lines
        for body in self.positionData:
            back2 = max(0, self.pointers[0])  # Set back2 to 0 if negative.
            self.ax1.plot(body[0][back2:self.pointers[1]],  # x values of current body being plotted.
                     body[1][back2:self.pointers[1]],  # y values '' ''
                     marker='o',  # Marker used to denote current position
                     markevery=[-1])  # Position of marker (second last)
        self.pointers[1] += 1  # increment front pointer
        self.pointers[0] = self.pointers[1] - self.expiry  # reset back pointer

    def play(self):
        self.playback_mode = not self.playback_mode
        if self.playback_mode:
            self.play_button.setText("Pause")
            self.ani.event_source.start()
            main.log("Simulation Played!")
            self.playback_mode = True
        else:
            self.play_button.setText("Play")
            self.pause()
            self.playback_mode = False


        if self.userBodies == []:
            main.log("No bodies configured.")
            return

        if self.data_gen_process == None:
            self.play_button.setEnabled(False)
            bodies = [body[0] for body in self.userBodies]  # Bodies to be simulated.
            for num, body in enumerate(bodies):
                bodies[num].id = num  # Assign unique id to all bodies being simulated
            manager = Manager()  # Shared multidimensional array manager accessible by both processes.
            self.positionData = manager.list()  # Shared multidimensional array
            self.data_gen = Value('i', 1)

            for body in bodies:
                self.positionData.append([[], []])  # Creates x y lists for each body in the body list.

            self.data_gen_process = Process(target=generate, args=(bodies, self.positionData, self.data_gen))
            # Must have trailing comma after final argument.
            self.data_gen_process.start()  # Spawn new process.
            main.log("Data gen process started: {}".format(self.data_gen_process.pid))
            self.play_button.setEnabled(True)


    def addMpl(self):
        self.fig = Figure()
        self.ax1 = self.fig.add_subplot(1, 1, 1)
        self.ax1.axis('equal')
        self.canvas = FigureCanvas(self.fig)  # Create canvas for figure.
        self.fig.set_facecolor('white')

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

    @pyqtSlot()
    def add_config(self):
        config = BodyConfig()
        config.delete_btn.clicked.connect(lambda: self.del_config(config))
        config.save.clicked.connect(lambda: self.SaveBody(config,
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




if __name__ == "__main__":
    app = QApplication(sys.argv)
    main = Main()
    main.addMpl()  # Add figure to the GUI
    # main.showMaximized() #Show GUI
    main.ani = animation.FuncAnimation(main.fig, main.animate)  # Create animation updating every 2ms.
    main.show()
    sys.exit(app.exec_())
