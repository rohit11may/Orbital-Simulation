# Orbital Simulation Practical Project
# Rohit Prasad
# 2016-2017
# Last changed on 11/12/2016


import multiprocessing
import matplotlib.animation as animation
import matplotlib.pyplot as plt
from random import randint
import numpy as np
from PyQt4.uic import loadUiType
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt4agg import (
    FigureCanvasQTAgg as FigureCanvas,
    NavigationToolbar2QT as NavigationToolbar)
import sys
from PyQt4 import QtGui


Ui_MainWindow, QMainWindow = loadUiType('..//GUI//window.ui')

def generate(x, y):
    for idx, n in enumerate(y):
        y[idx] = randint(0, 10) # Generates a random number from 1 to 10.
        x[idx] = idx

def animate(i):
    global x #Use global to avoid the use of 'x' in the namespace of animate()
    global y
    global pos
    ax1.clear()
    ax1.plot(x[0:pos], y[0:pos]) #Plot only up to a certain point of the arrays.
    pos += 1

class Main(QMainWindow, Ui_MainWindow):
    def __init__(self, ):
        super(Main, self).__init__()
        self.setupUi(self)

    def addMpl(self, fig):
        self.canvas = FigureCanvas(fig) # Create canvas for figure.
        self.mplvl.addWidget(self.canvas) # Add canvas as widget to mplvl
        self.canvas.draw() # Draw canvas


if __name__ == "__main__":

    app = QtGui.QApplication(sys.argv)
    main = Main()

    fig = Figure()
    ax1 = fig.add_subplot(1, 1, 1)
    main.addMpl(fig) #Add figure to the GUI
    main.show() #Show GUI

    y = multiprocessing.Array('d', 1000) # Created shared memory space.
    x = multiprocessing.Array('d', 1000)
    pos = 0

    p = multiprocessing.Process(target=generate, args=(x, y,))
    p.start() #Spawn new process.

    ani = animation.FuncAnimation(fig, animate, interval=3) # Create animation updating every 3ms.

    sys.exit(app.exec_())