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
        y[idx] = randint(0, 10)
        x[idx] = idx


def animate(i):
    global x
    global y
    global pos
    ax1.clear()
    ax1.plot(x[0:pos], y[0:pos])
    pos += 1

class Main(QMainWindow, Ui_MainWindow):
    def __init__(self, ):
        super(Main, self).__init__()
        self.setupUi(self)

    def addmpl(self, fig):
        self.canvas = FigureCanvas(fig)
        self.mplvl.addWidget(self.canvas)
        self.canvas.draw()


if __name__ == "__main__":

    app = QtGui.QApplication(sys.argv)
    main = Main()

    fig = Figure()
    ax1 = fig.add_subplot(1, 1, 1)
    main.addmpl(fig)
    main.show()

    y = multiprocessing.Array('d', 1000)
    x = multiprocessing.Array('d', 1000)
    pos = 0
    p = multiprocessing.Process(target=generate, args=(x, y,))
    p.start()

    ani = animation.FuncAnimation(fig, animate, interval=3)

    sys.exit(app.exec_())