# @author Shelton Ngwenya, R00203947
# receiver class

import random as random

import wsnsimpy.wsnsimpy as wsp
from node_messages import NodeMessages


class Device(wsp.Node):  # All nodes are sub-classes of wsp.Node
    def __init__(self, sim, id, pos):  # "__init__"
        # constructor of the node, initialise the super class
        super().__init__(sim, id, pos)
        # instantiate the physical layer for the node
        self.phy = wsp.DefaultPhyLayer(self)
        self.mac = self  # node object will act as a MAC layer
        self.tx_range = 150  # transmission range of the node
        self.slot_position = -1  # device slot
        self.slot_delay = -1  # device slot transmission delay

    def init(self):
        super().init()
        self.logging = True

    def node_status(self, *args, **kwargs):
        # initial period
        self.log(f"{kwargs['status']}")

    def transmission_delay(self, transmit_delay):
        self.sim.delayed_exec(
            transmit_delay, self.transmission_delay, transmit_delay)
        mystr = NodeMessages.DATA
        self.delay_response(mystr)

    def delay_response(self, mystr):

        response_pdu = wsp.PDU(None,
                               # Size in bits is 8 x length of mystr
                               len(mystr) * 8,
                               data=mystr,
                               source=self.id,
                               dest=1,
                               packet_type=2
                               )

        # send the response pdu
        self.phy.send_pdu(response_pdu)

    def on_receive_pdu(self, pdu):  # inspect, log (print), or process the PDU fields
        # check if packet data equal to BS_HELLO
        if pdu.data == NodeMessages.BS_HELLO:
            self.node_status(
                status=f"{NodeMessages.RECEIVED_PDU_FROM} {pdu.source}: {pdu.data}")
            # generate a random timeout value
            random_timeout = random.random() * .1
            # send a pdu to base station in a scattered manner to avoid collisions
            self.sim.delayed_exec(
                random_timeout, self.delay_response, mystr=NodeMessages.DEV_HELLO)

        # check if packet type is data equal to BS_HELLO
        if pdu.data == NodeMessages.SCHED:
            self.node_status(
                status=f"{NodeMessages.RECEIVED_PDU_FROM} {pdu.source}: {pdu.data}")
            # check if device has been allocated a slot
            if self.id in pdu.dev_slots:
                # get the device slot's position
                slot_position = pdu.dev_slots.index(self.id)
                self.slot_position = slot_position
                # get the device slot's delay
                self.slot_delay = pdu.start_delay
                self.node_status(
                    status=f"{NodeMessages.HAS_SLOT} {slot_position}")
                transmit_delay = self.slot_delay + self.slot_position * .1
                # transmit a sched pdu back to base station
                self.sim.delayed_exec(
                        transmit_delay, self.transmission_delay, transmit_delay)
            else:
                self.node_status(
                    status=f"{NodeMessages.NO_SLOT}")

    def run(self):
        self.node_status(status=f"{NodeMessages.WAITING_HELLO}")
