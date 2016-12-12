# Orbital Simulation Practical Project
# Rohit Prasad
# 2016-2017
# Last changed on 11/12/2016

import logging
from src.vector import Vector
from src.body import Body


def force(a, b):
    if isinstance(a, Body) and isinstance(b, Body):
        pass
    else:
        logging.critical
