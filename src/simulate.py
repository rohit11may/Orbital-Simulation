# Orbital Simulation Practical Project
# Rohit Prasad
# 2016-2017
# Last changed on 11/12/2016

# Shared Memory
import multiprocessing
import matplotlib.animation as animation
import matplotlib.pyplot as plt
from random import randint
import time


def generate(x, y):
    for idx, n in enumerate(y):
        y[idx] = randint(0, 10)
        x[idx] = idx


def animate(i):
    global x
    global y
    global pos
    ax1.clear()
    ax1.plot(x[0:pos], y[0:pos])
    pos += 1


if __name__ == "__main__":
    fig = plt.figure()
    ax1 = fig.add_subplot(1, 1, 1)

    y = multiprocessing.Array('d', 1000)
    x = multiprocessing.Array('d', 1000)
    pos = 0

    p = multiprocessing.Process(target=generate, args=(x, y,))
    p.start()

    ani = animation.FuncAnimation(fig, animate, interval=3)
    plt.show()