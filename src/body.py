# Orbital Simulation Practical Project
# Rohit Prasad
# 2016-2017
# Last changed on 10/12/2016

import logging
from src.vector import Vector



class Body(object):
    def __init__(self, id, name, mass, position, velocity, type):
        self._id = id
        self._name = name
        self._mass = mass
        self._position = position
        self._velocity = velocity
        self._type = type

        self._acceleration = Vector(0, 0)

    def updateSelf(self, force, dt):
        pass

    #Getters
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

    #Setters
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

