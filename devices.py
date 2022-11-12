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
        self.slot_position = -1 # device slot p

    def init(self):
        super().init()
        self.logging = True

    def node_status(self, *args, **kwargs):
        # initial period
        self.log(f"{kwargs['status']}")

    def delay_response(self):

        # create response pdu "DEV-HELLO"
        mystr = NodeMessages.DEV_HELLO
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
                random_timeout, self.delay_response)

        # check if packet type is data equal to BS_HELLO
        if pdu.data == NodeMessages.SCHED:
            self.node_status(
                status=f"{NodeMessages.RECEIVED_PDU_FROM} {pdu.source}: {pdu.data}")
            # check if device has been allocated a slot
            if self.id in pdu.dev_slots:
                # get the slot's position
                slot_position = [x for x in range(len(pdu.dev_slots)) if pdu.dev_slots[x] == self.id]
                self.slot_position = slot_position
                self.node_status(
                    status=f"{NodeMessages.HAS_SLOT} {slot_position}")
            else:
                self.node_status(
                    status=f"{NodeMessages.NO_SLOT}")

    def run(self):
        self.node_status(status=f"{NodeMessages.WAITING_HELLO}")
