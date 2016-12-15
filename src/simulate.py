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

AU = 149598e6
logging.basicConfig(format='%(asctime)s.%(msecs)03d // %(message)s',
                    filename="..//logs//logfile.log",
                    datefmt='%H:%M:%S',
                    filemode='w',
                    level=logging.DEBUG)

Ui_MainWindow, QMainWindow = loadUiType('..//GUI//window.ui')  # Load UI file from GUI folder.
UI_BodyConfigMainWindow, BodyConfigMainWindow = loadUiType('..//GUI//body_config_widget.ui')  # Load UI file from GUI folder.


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

def animate(i):
    global positionData
    global pointers
    global expiry
    ax1.clear()  # clear lines

    for body in positionData:
        back2 = max(0, pointers[0])  # Set back2 to 0 if negative.
        ax1.plot(body[0][back2::],  # x values of current body being plotted.
                 body[1][back2::],  # y values '' ''
                 marker='o',  # Marker used to denote current position
                 markevery=[-1])  # Position of marker (second last)

    pointers[1] += 100  # increment front pointer
    pointers[0] = pointers[1] - expiry  # reset back pointer

def on_click():
    print("Hello World")

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
        self.config_widgets.append(config)
        self.bodyConfig.addWidget(self.config_widgets[-1])

    @pyqtSlot()
    def del_config(self, widget):
        self.bodyConfig.removeWidget(widget)
        widget.deleteLater()
        widget = None

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


    bodies = [lib.Pluto, lib.Charon]  # Bodies to be simulated.
    manager = Manager()  # Shared multidimensional array manager accessible by both processes.
    positionData = manager.list()  # Shared multidimensional array
    for body in bodies:
        positionData.append([[], []])  # Creates x y lists for each body in the body list.

    p = Process(target=generate, args=(bodies, positionData,))  # Creates process p for data generation
    # Must have trailing comma after final argument.
    expiry = 3000000
    pointers = [0 - expiry, 0]  # Plotting Pointers
    # p.start()  # Spawn new process.
    ani = animation.FuncAnimation(fig, animate)  # Create animation updating every 2ms.
    sys.exit(app.exec_())
