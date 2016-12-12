# Orbital Simulation Practical Project
# Rohit Prasad
# 2016-2017
# Last changed on 11/12/2016

import logging
from src.vector import Vector
from src.body import Body

G = 6.674 * (10**-11)

def distance(a, b):
    if isinstance(a, Body) and isinstance(b, Body):
        x_diff = a.position.get()[0] - b.position.get()[0]
        y_diff = a.position.get()[1] - b.position.get()[1]
        dist = ((x_diff**2) + (y_diff**2))**0.5
        logging.debug("Distance returned: {}".format(str(dist)))
        return dist
    else:
        logging.WARNING("Distance calculation is not between two bodies: {} / {}".format(a, b))

def force(a, b):
    if isinstance(a, Body) and isinstance(b, Body):
        dist = distance(a, b)
        force_val = (G * a.mass * b.mass) / (dist ** 2)
        logging.debug("Force returned: {}".format(str(force_val)))
        return force_val
    else:
        logging.WARNING("Force calculation is not between two bodies: {} / {}".format(a, b))
