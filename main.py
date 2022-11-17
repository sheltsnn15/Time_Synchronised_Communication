# @author Shelton Ngwenya, R00203947
import random as random

import wsnsimpy.wsnsimpy as wsp

from base_station import BaseStation
from devices import Device

sim = wsp.Simulator(
    until=50,  # length of simulation (seconds)
    timescale=1  # 1 is real time, 0 is as fast as possible
)

transmitter_node = sim.add_node(
    BaseStation,  # Python class of the node
    (50, 50)  # random (x, y) position coordinates
)

for i in range(0, 10):
    device_nodes = sim.add_node(
        Device,  # Python class of the node
        # random (x, y) position coordinates
        (random.random() * 100, random.random() * 100)
    )


if __name__ == '__main__':
    sim.run()
    # n1 stats: TX=2 RX=358Collisions=2
    print(f"Number of collisions={transmitter_node.phy.stat.total_collision}")

"""
 
"""

