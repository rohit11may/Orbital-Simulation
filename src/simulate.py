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
import multiprocessing

# Matplotlib
import matplotlib.animation as animation
from matplotlib.figure import Figure

# Others
from random import randint
from src.body import Body
from src.vector import Vector
import sys
import logging



Ui_MainWindow, QMainWindow = loadUiType('..//GUI//window.ui') # Load UI file from GUI folder.


def generate(x, y):
    for idx, n in enumerate(y):
        y[idx] = randint(0, 10) # Generates a random number from 1 to 10.
        x[idx] = idx

def animate(i):
    global x #Use global to avoid the use of 'x' in the namespace of animate()
    global y
    global pos
    global main
    ax1.clear()
    ax1.plot(x[0:pos], y[0:pos]) #Plot only up to a certain point of the arrays.
    pos += 1
    # main.log("x: {} ¦ y: {}".format(str(x[pos]),str(y[pos])))
    main.updateProgressBar((pos/1000)*100)

class Main(QMainWindow, Ui_MainWindow): # Go to Form -> View Code in QTDesigner to see structure of GUI.
    def __init__(self, ):
        super(Main, self).__init__()
        self.setupUi(self)

        # Setup console box
        self.textEdit = QtGui.QTextEdit()
        self.console_box.setWidget(self.textEdit)
        logging.info("Setup console box.")

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
        logging.info(text)

    def updateProgressBar(self, value):
        self.loading_bar_widget.setValue(value)


if __name__ == "__main__":

    app = QtGui.QApplication(sys.argv)
    main = Main()

    fig = Figure()
    ax1 = fig.add_subplot(1, 1, 1)

    main.addMpl(fig) # Add figure to the GUI
    main.addToolBar() # Add toolbar to the GUI; MUST BE CALLED AFTER .addMpl()
    main.showMaximized() #Show GUI
    main.show()

    # Configure Earth Body
    Earth = Body()
    Earth.id = 1
    Earth.name = "Earth"
    Earth.mass = 5.98 * (10 ** 24)
    Earth.position = Vector()
    Earth.position.set(150000000000, 0)
    Earth.velocity = Vector()
    Earth.velocity.set(0, 29.8 * (10 ** 3))
    Earth.type = "Planet"
    main.log(str(Earth))

    # Configure Sun Body
    Sun = Body()
    Sun.id = 1
    Sun.name = "Sun"
    Sun.mass = 1.989 * (10 ** 30)
    Sun.position = Vector()
    Sun.position.set(0,0)
    Sun.velocity = Vector()
    Sun.velocity.set(0, 0)
    Sun.type = "Star"

    bodies = [Sun, Earth]
    main.log(str(Sun))
    positionData = []

    for body in bodies:
        positionData.append([multiprocessing.Array('d', 10000), multiprocessing.Array('d', 10000)])


    p = multiprocessing.Process(target=generate, args=(bodies, positionData,))
    # Must have trailing comma after final argument.

    p.start() #Spawn new process.

    ani = animation.FuncAnimation(fig, animate, interval=50) # Create animation updating every 3ms.
    sys.exit(app.exec_())

