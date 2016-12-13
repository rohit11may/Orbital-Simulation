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
from multiprocessing import Process, Manager

# Matplotlib
import matplotlib.animation as animation
from matplotlib.figure import Figure

# Local
from src.body import Body
from src.orbitmath import calculate_resultant_force
from src.vector import Vector

# Others
import sys
import logging


AU = 149598e6
logging.basicConfig(format='%(asctime)s.%(msecs)03d // %(message)s',
                    filename="..//logs//logfile.log",
                    datefmt='%H:%M:%S',
                    filemode='w',
                    level=logging.DEBUG)

Ui_MainWindow, QMainWindow = loadUiType('..//GUI//window.ui') # Load UI file from GUI folder.



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
    ax1.clear() # clear lines

    for body in positionData:
        back2 = max(0, pointers[0]) #Set back2 to 0 if negative.
        ax1.plot(body[0][back2:pointers[1]], # x values of current body being plotted.
                 body[1][back2:pointers[1]], # y values '' ''
                 marker = 'o', # Marker used to denote current position
                 markevery=[-1]) # Position of marker (second last)

    pointers[1] += 1 # increment front pointer
    pointers[0] = pointers[1] - expiry # reset back pointer


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



if __name__ == "__main__":

    app = QtGui.QApplication(sys.argv)
    main = Main()

    fig = Figure()
    ax1 = fig.add_subplot(1, 1, 1)
    ax1.axis('equal')
    main.addMpl(fig) # Add figure to the GUI
    main.addToolBar() # Add toolbar to the GUI; MUST BE CALLED AFTER .addMpl()
    # main.showMaximized() #Show GUI
    main.show()

    # Configure Earth Body
    Earth = Body()
    Earth.id = 1
    Earth.name = "Earth"
    Earth.mass = 5.972e24
    Earth.position.set(AU, 0)
    Earth.velocity = Vector()
    Earth.velocity.set(0, 29.8e3)
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

    # Configure Mars Body
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

    # Configure Jupiter Body
    Jupiter = Body()
    Jupiter.id = 5
    Jupiter.name = "Jupiter"
    Jupiter.mass = 1.90e27
    Jupiter.position.set(5.455 * AU, 0)
    Jupiter.velocity.set(0, 12.44e3)
    Jupiter.type = "Planet"
    main.log(str(Jupiter))

    bodies = [Sun, Earth, Mars, Halley]
    manager = Manager()
    positionData = manager.list()
    for body in bodies:
        positionData.append([[], []])

    p = Process(target=generate, args=(bodies, positionData,))
    # Must have trailing comma after final argument.
    expiry = 3000000
    pointers = [0 - expiry, 0]
    p.start() #Spawn new process.
    ani = animation.FuncAnimation(fig, animate) # Create animation updating every 2ms.
    sys.exit(app.exec_())

