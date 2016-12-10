# Orbital Simulation Practical Project
# Rohit Prasad
# 2016-2017
# Last changed on 10/12/2016


from math import (atan, degrees)
import logging
# Logging configuration : May need to be moved to a separate file.
# 15:06:06.928 // Earth: Mass must be a float: Value = e Type = <class 'str'> Example log file.
# Filemode = 'w' ensures the log file is reset on execution.

logging.basicConfig(format='%(asctime)s.%(msecs)03d // %(message)s',
                    filename="logfile.log",
                    datefmt='%H:%M:%S',
                    filemode='w',
                    level=logging.WARNING)

# When creating a vector object, it instantiates as a zero vector.
# Use setter method to assign values.

class Vector(object):

    def __init__(self):
        self.x = 0
        self.y = 0

    def get(self):
        return (self.x, self.y)

    def set(self, x, y):
        if isinstance(x, float) and isinstance(y, float): #Ensures that x and y are integers, when set.
            self.x = x
            self.y = y
        else:
            logging.warning("Coords must be floats: x = {} y = {} ¦ xTyp = {} yTyp = {}".format(x,y,type(x),type(y)))

    #Returns magnitude of vector object.
    def getMagnitude(self):
        return ((self.x ** 2) + (self.y ** 2)) ** 0.5

    #Returns direction in DEGREES of vector object.
    def getDirection(self):
        return degrees(atan(self.y / self.x))

    #Adds another vector object to self, verifies the addition is between vectors.
    def add(self, value):
        if isinstance(value, Vector):
            self.x += value.x
            self.y += value.y
        else:
            logging.warning("Addition must be with vector: Value = {} ¦ Type = {}".format(value, type(value)))

    # Divides a vector by a scalar, verifies the division is between vector and scalar.
    def divide(self, value):
        if isinstance(value, float):
            self.x /= value
            self.y /= value
        else:
            logging.warning("Division must be with scalar: Value = {} ¦ Type = {}".format(value, type(value)))

    # Multiplies a vector by a scalar, verifies the multiplication is between vector and scalar
    def multiply(self, value):
        if isinstance(value, float):
            self.x *= value
            self.y *= value
        else:
            logging.warning("Multiplication must be with scalar: Value = {} ¦ Type = {}".format(value, type(value)))