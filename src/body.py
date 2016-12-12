# Orbital Simulation Practical Project
# Rohit Prasad
# 2016-2017
# Last changed on 12/12/2016

import logging
from src.vector import Vector #imports the vector class from Vector.py

logging.basicConfig(format='%(asctime)s.%(msecs)03d // %(message)s',
                    filename="..//logs//logfile.log",
                    datefmt='%H:%M:%S',
                    filemode='w',
                    level=logging.DEBUG)

class Body(object):
    def __init__(self):
        self._id = "" #id initialised to empty string.
        self._name = "" # Name initialised to empty string.
        self._mass = 0 # Mass initialised to 0.
        self._position = Vector() # Position initialised to zero vector.
        self._velocity = Vector() # Velocity initialised to zero vector.
        self._type = "" #Type initialised to empty string.
        self._acceleration = Vector() # Acceleration initialised to 0

    def __repr__(self):
        return "Name: {} \n" \
               "Mass: {} \n" \
               "Position: {} \n" \
               "Velocity: {} \n" \
               "-----------".format(self.name, self.mass, self.position, self.velocity)

    def updateSelf(self, force, dt=8000):
        self.acceleration = force.divide(self.mass)

        self.velocity.add(self.acceleration.multiply(dt))

        self.position.add(self.velocity.multiply(dt))

    #Getter functions. @property avoids the need to use the getter and setter function calls when using it in code.
    @property
    def id(self):
        return self._id

    @property
    def name(self):
        return self._name

    @property
    def mass(self):
        return self._mass

    @property
    def position(self):
        return self._position

    @property
    def velocity(self):
        return self._velocity

    @property
    def acceleration(self):
        return self._acceleration

    @property
    def type(self):
        return self._type

    #Setter functions. Uses .setter suffix to denote the setter functions. E.g. "body.id" will call the setter below.
    @id.setter
    def id(self, value):
        self._id = value

    @name.setter
    def name(self, value):
        self._name = value

    @mass.setter
    def mass(self, value):
        if isinstance(value, float):
            self._mass = value
        else:
            logging.critical("{}: Mass must be a float: Value = {} Type = {}".format(self.name, value, type(value)))

    @position.setter
    def position(self, value):
        if isinstance(value, Vector):
            self._position = value
        else:
            logging.critical("{}: Position must be a vector: Value = {} Type = {}".format(self.name, value, type(value)))

    @velocity.setter
    def velocity(self, value):
        if isinstance(value, Vector):
            self._velocity= value
        else:
            logging.critical("{}: Velocity must be a vector: Value = {} Type = {}".format(self.name, value, type(value)))

    @acceleration.setter
    def acceleration(self, value):
        if isinstance(value, Vector):
            self._acceleration = value
        else:
            logging.critical("{}: Acceleration must be a vector: Value = {} Type = {}".format(self.name, value, type(value)))

    @type.setter
    def type(self, value):
        if value in ["Star", "Comet", "Planet", "Moon", "Other"]:
            self._type = value
        else:
            logging.warning("{}: Type must be valid: Value = {}".format(self.name, value))