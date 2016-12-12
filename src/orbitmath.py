# Orbital Simulation Practical Project
# Rohit Prasad
# 2016-2017
# Last changed on 11/12/2016

import logging
from src.body import Body

G = 6.674 * (10**-11)

logging.basicConfig(format='%(asctime)s.%(msecs)03d // %(message)s',
                    filename="..//logs//logfile.log",
                    datefmt='%H:%M:%S',
                    filemode='w',
                    level=logging.DEBUG)

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
        logging.warning("Force calculation is not between two bodies: {} / {}".format(a, b))


def calculate_resultant_force(all_bodies, req_body):
    resultant_force = 0
    # print("ALL BODIES: {} \n"
    #       "REQ BODY: {}".format(all_bodies, req_body))
    for body in all_bodies:
        if body.id != req_body.id:
            resultant_force += force(body, req_body)
    return resultant_force