# Orbital Simulation Practical Project
# Rohit Prasad
# 2016-2017
# Last changed on 11/12/2016

# GUI Libraries.
from PyQt4 import QtGui
from PyQt4.uic import loadUiType
from matplotlib.backends.backend_qt4agg import (
    FigureCanvasQTAgg as FigureCanvas,
    NavigationToolbar2QT as NavigationToolbar)

# Multiprocessing module.
from multiprocessing import Process, Array, Pipe, Pool, Manager

# Matplotlib
import matplotlib.animation as animation
from matplotlib.figure import Figure

# Local
from src.body import Body
from src.orbitmath import calculate_resultant_force, return_positions
from src.vector import Vector

# Others
import sys
import logging
import time
from functools import partial # To tie arguments together for pooling.
AU = 149598e6
logging.basicConfig(format='%(asctime)s.%(msecs)03d // %(message)s',
                    filename="..//logs//logfile.log",
                    datefmt='%H:%M:%S',
                    filemode='w',
                    level=logging.DEBUG)

Ui_MainWindow, QMainWindow = loadUiType('..//GUI//window.ui') # Load UI file from GUI folder.



def generate(bodies, positionData):
    idx = 0
    noOfProcesses = len(bodies)
    while idx <= 10000:

        for num, body in enumerate(bodies):
            temp_body = calculate_resultant_force(bodies, body)
            bodies[num] = temp_body
            x = positionData[num][0]
            x.append(temp_body.position.get()[0])
            y = positionData[num][1]
            y.append(temp_body.position.get()[1])
            positionData[num] = [x, y]
        idx += 1


def animate(i):
    global positionData
    global pos
    global main
    ax1.clear()
    for body in positionData:
        ax1.plot(body[0][0:pos], body[1][0:pos]) #Plot only up to a certain point of the arrays.
    pos += 1
    # main.log("x: {} ¦ y: {}".format(str(x[pos]),str(y[pos])))
    # main.updateProgressBar((pos/1000)*100)

class Main(QMainWindow, Ui_MainWindow): # Go to Form -> View Code in QTDesigner to see structure of GUI.
    def __init__(self, ):
        super(Main, self).__init__()
        self.setupUi(self)

        # Setup console box
        self.textEdit = QtGui.QTextEdit()
        self.console_box.setWidget(self.textEdit)
        logging.info("Setup Console Box")

    def addMpl(self, fig):
        self.canvas = FigureCanvas(fig) # Create canvas for figure.
        fig.set_facecolor('white')
        self.mplvl.addWidget(self.canvas) # Add canvas as widget to mplvl layout in window.ui file.
        self.canvas.draw() # Draw canvas
        logging.info("Added Matplotlib graph.")

    def addToolBar(self):
        # Setup toolbar
        self.toolbar = NavigationToolbar(self.canvas, self.mplwindow, coordinates=True) #Instantiate toolbar.
        self.toolbar_container.addWidget(self.toolbar) #Add toolbar to layout.
        logging.info("Added toolbar")

    def log(self, text):
        self.textEdit.append(text)
        logging.debug(text)

    def updateProgressBar(self, value):
        self.loading_bar_widget.setValue(value)


if __name__ == "__main__":

    app = QtGui.QApplication(sys.argv)
    main = Main()

    fig = Figure()
    ax1 = fig.add_subplot(1, 1, 1)

    ax1.plot(-175*(10**9),-175*(10**9))
    ax1.plot(175*(10**9),175*(10**9))
    # ax1.autoscale_view(False, False, False)
    # axes = fig.gca()
    # axes.set_xlim([-150*(10**9), 150*(10**9)])
    # axes.set_ylim([-150*(10**9), 150*(10**9)])

    main.addMpl(fig) # Add figure to the GUI
    main.addToolBar() # Add toolbar to the GUI; MUST BE CALLED AFTER .addMpl()
    # main.showMaximized() #Show GUI
    main.show()

    # Configure Earth Body
    Earth = Body()
    Earth.id = 1
    Earth.name = "Earth"
    Earth.mass = 5.972 * (10 ** 24)
    Earth.position.set(149600000000, 0)
    Earth.velocity = Vector()
    Earth.velocity.set(0, 29.8 * (10 ** 3))
    Earth.type = "Planet"
    main.log(str(Earth))

    # Configure Sun Body
    Sun = Body()
    Sun.id = 2
    Sun.name = "Sun"
    Sun.mass = 1.989e30
    Sun.position.set(0,0)
    Sun.velocity.set(0,0)
    Sun.type = "Star"
    main.log(str(Sun))

    # Configure third Body
    Mars = Body()
    Mars.id = 3
    Mars.name = "Mars"
    Mars.mass = 4.02e22
    Mars.position.set(227.9e9, 0)
    Mars.velocity.set(0,24.1308e3)
    Mars.type = "Planet"
    main.log(str(Mars))

    # Configure Halley's comet
    Halley = Body()
    Halley.id = 4
    Halley.name = "Halley"
    Halley.mass = 2.2e14
    Halley.velocity.set(-50e3, 0)
    Halley.position.set(0, 88e9)
    Halley.type = "Comet"
    main.log(str(Halley))


    bodies = [Sun, Earth, Mars, Halley]
    manager = Manager()
    positionData = manager.list()
    for body in bodies:
        positionData.append([[], []])

    p = Process(target=generate, args=(bodies, positionData,))
    # Must have trailing comma after final argument.

    p.start() #Spawn new process.
    pos = 0
    ani = animation.FuncAnimation(fig, animate, interval=0) # Create animation updating every 2ms.
    sys.exit(app.exec_())

