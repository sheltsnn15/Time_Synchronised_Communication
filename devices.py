# receiver class

import random as random

import wsnsimpy.wsnsimpy as wsp


class Device(wsp.Node):  # All nodes are sub-classes of wsp.Node
    def __init__(self, sim, id, pos):  # "__init__"
        # constructor of the node, initialise the super class
        super().__init__(sim, id, pos)
        # instantiate the physical layer for the node
        self.phy = wsp.DefaultPhyLayer(self)
        self.mac = self  # node object will act as a MAC layer
        self.tx_range = 100  # transmission range of the node

    def init(self):
        super().init()
        self.logging = True
