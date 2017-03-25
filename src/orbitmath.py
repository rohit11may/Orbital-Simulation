# Orbital Simulation Practical Project
# Rohit Prasad
# 2016-2017
# Last changed on 25/03/2016

import logging
from math import atan2, cos, sin
from src.body import Body
from src.vector import Vector

G = 6.674e-11

logging.basicConfig(format='%(asctime)s.%(msecs)03d // %(message)s',
                    filename="..//logs//logfile.log",
                    datefmt='%H:%M:%S',
                    filemode='w',
                    level=logging.DEBUG)

# == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == ==
# DISTANCE
# == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == ==

def distance(a, b):
    '''
    Calculates distance in metres between two bodies.
    '''
    if isinstance(a, Body) and isinstance(b, Body):
        x_diff = a.position.get()[0] - b.position.get()[0]
        y_diff = a.position.get()[1] - b.position.get()[1]
        difference = Vector()
        difference.set(x_diff, y_diff)
        return difference
    else:
        logging.WARNING("Distance calculation is not between two bodies: {} / {}".format(a, b))

'''
The above code first ensures that it is dealing with two Body objects. Next it calculates the difference in x position
and y position. These differences are assigned to a new vector object and returned.
'''

# == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == ==
# FORCE
# == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == ==

def force(a, b):
    '''
    Calculates gravitational force of attraction between two bodies.
    '''
    if isinstance(a, Body) and isinstance(b, Body):
        dist = distance(a, b) # Calculate distance
        force_val = (G * a.mass * b.mass) / (dist.getMagnitude() ** 2) # Use formula for gravitation
        dx, dy = dist.get()

        theta = atan2(dy, dx) # Find angle at which the force acts.

        Fx, Fy = force_val * cos(theta), force_val * sin(theta) # Calculate components of force
        force_val = Vector()
        force_val.set(Fx, Fy) # Create new vector object
        return force_val # Return vector object
    else:
        logging.warning("Force calculation is not between two bodies: {} / {}".format(a, b))

'''
The above code block first uses F = G * M1 * M2 / (r^2) to calculate the force between the two bodies 'a' and 'b'.
Next it finds the components of the force in the x direction and the y direction and assigns them to a force vector
object. This vector object is returned.
'''

# == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == ==
# RESULTANT FORCE
# == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == == ==

def calculate_resultant_force(all_bodies, req_body, dt):
    '''
    Calculates the resultant force a body is experiencing.
    '''
    resultant_force = Vector()

    for body in all_bodies:
        if body.id != req_body.id:
            resultant_force.add(force(body, req_body))
    req_body.updateSelf(resultant_force, dt=dt)
    return req_body

'''
The above code block calculates the resultant force on the req_body by adding calculating the gravitational force of
attraction between req_body and all other bodies being simulated, and adding them up. It returns an updated body object,
after accounting for the time step.
'''
