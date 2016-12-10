# Orbital Simulation Practical Project
# Rohit Prasad
# 2016-2017
# Last changed on 10/12/2016


from math import (atan, degrees)
import logging
logging.basicConfig(format='%(asctime)s.%(msecs)03d // %(message)s',
                    filename="logfile.log",
                    datefmt='%H:%M:%S',
                    filemode='w',
                    level=logging.WARNING)

class Vector(object):

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def get(self):
        return (self.x, self.y)

    def set(self, x, y):
        if isinstance(x, float) and isinstance(y, float):
            self.x = x
            self.y = y
        else:
            logging.warning("Coordinates must be floats: xVal = {} yVal = {} ¦ xTyp = {} yTyp = {}".format(x,y,type(x),type(y)))

    def getMagnitude(self):
        return ((self.x ** 2) + (self.y ** 2)) ** 0.5

    def getDirection(self):
        return degrees(atan(self.y / self.x))

    def add(self, value):
        if isinstance(value, Vector):
            self.x += value.x
            self.y += value.y
        else:
            logging.warning("Addition must be with vector: Value = {} ¦ Type = {}".format(value, type(value)))

    def divide(self, value):
        if isinstance(value, float):
            self.x /= value
            self.y /= value
        else:
            logging.warning("Division must be with scalar: Value = {} ¦ Type = {}".format(value, type(value)))

    def multiply(self, value):
        if isinstance(value, float):
            self.x *= value
            self.y *= value
        else:
            logging.warning("Multiplication must be with scalar: Value = {} ¦ Type = {}".format(value, type(value)))