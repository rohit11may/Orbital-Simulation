# Orbital Simulation Practical Project
# Rohit Prasad
# 2016-2017
# Last changed on 12/12/2016


from math import (atan, degrees)
import logging
# Logging configuration : May need to be moved to a separate file.
# 15:06:06.928 // Earth: Mass must be a float: Value = e Type = <class 'str'> Example log file.
# Filemode = 'w' ensures the log file is reset on execution.

logging.basicConfig(format='%(asctime)s.%(msecs)03d // %(message)s',
                    filename="..//logs//logfile.log",
                    datefmt='%H:%M:%S',
                    filemode='w',
                    level=logging.DEBUG)

# When creating a vector object, it instantiates as a zero vector.
# Use setter method to assign values.

class Vector(object):

    def __init__(self):
        self.x = 0
        self.y = 0

    def __repr__(self):
        return("x: {} ¦ y: {}".format(str(self.x), str(self.y)))

    def get(self):
        return (self.x, self.y)

    def set(self, x, y):
        if isinstance(x, (float, int)) and isinstance(y, (float, int)): #Ensures that x and y are floats, when set.
            self.x = x
            self.y = y
        else:
            logging.warning("Co-ords must be floats: x = {} y = {} ¦ xTyp = {} yTyp = {}".format(str(x),str(y)
                                                                                                ,type(x),type(y)))

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
        if isinstance(value, (float, int)):
            ans = Vector()
            ans.set(self.x / value, self.y / value)
            return ans
        else:
            logging.warning("Division must be with scalar: Value = {} ¦ Type = {}".format(value, type(value)))

    # Multiplies a vector by a scalar, verifies the multiplication is between vector and scalar
    def multiply(self, value):
        if isinstance(value, (float, int)):
            ans = Vector()
            ans.set(self.x * value, self.y * value)
            return ans
        else:
            logging.warning("Multiplication must be with scalar: Value = {} ¦ Type = {}".format(value, type(value)))

