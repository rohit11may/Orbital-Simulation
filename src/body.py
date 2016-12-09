__author__ = 'Rohit'

# Orbital Simulation Practical Project
# Rohit Prasad
# 2016-2017
# Last changed on 09/12/2016


class Body():
    def __init__(self, id, name, mass, position, velocity, acceleration, type):
        self._id = id
        self._name = name
        self._mass = mass
        self._position = position
        self._velocity = velocity
        self._acceleration = acceleration
        self._type = type

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
        print("HEY")
        self._id = value

    @name.setter
    def name(self, value):
        self._name = value

    @mass.setter
    def mass(self, value):
        self._mass = value

    @position.setter
    def position(self, value):
        self._position = value

    @velocity.setter
    def velocity(self, value):
        self._velocity = value

    @acceleration.setter
    def acceleration(self, value):
        self._acceleration = value

    @type.setter
    def type(self, value):
        self._type = value
