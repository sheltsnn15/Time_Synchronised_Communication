# transmitter class

import random as random

import wsnsimpy.wsnsimpy as wsp
from node_messages import NodeMessages


class BaseStation(wsp.Node):  # All nodes are sub-classes of wsp.Node
    def __init__(self, sim, id, pos):  # "__init__"
        # constructor of the node, initialise the super class
        super().__init__(sim, id, pos)
        # instantiate the physical layer for the node
        self.phy = wsp.DefaultPhyLayer(self)
        self.mac = self  # node object will act as a MAC layer
        self.tx_range = 150  # transmission range of the node
        self.cancelled_execution = False  # flag to see if ACK received
        self.device_counter = 0
        self.dev_slots = []

    def init(self):
        super().init()
        self.logging = True

    def node_status(self, *args, **kwargs):  # view the status of each node in the network
        self.log(f"{kwargs['status']}")

    def add_device_slots(self, pdu):  # dedicate each device to a schedule slot
        self.dev_slots.insert(self.device_counter, pdu.source)

    def display_device_slots(self, *args, **kwargs):  # display devices and their scheduled slots
        elements = []
        for index, item in enumerate(kwargs['device_slots']):
            elements.append(f"({item}, {index})")
        self.log(f"{elements}")

    def on_receive_pdu(self, pdu):  # inspect, log (print), or process the PDU fields
        # check pdu data for each node transmission received
        if pdu.data == NodeMessages.DEV_HELLO:
            # count number of devices that sent dev_hello message
            self.device_counter += 1
            # add devices to the schedule device slot
            self.add_device_slots(pdu)
            self.node_status(
                status=f"{NodeMessages.RECEIVED_PDU_FROM} {pdu.source}: {pdu.data}")
        if pdu.data == NodeMessages.DATA:
            #yield self.timeout(5)
            # data period
            self.node_status(
                status=f"{NodeMessages.RECEIVED_PDU_FROM} {pdu.source}: {pdu.data}")

    def run(self):
        # discovery period pdu
        bs_hello_str = NodeMessages.BS_HELLO
        discovery_pdu = wsp.PDU(None,
                                # Size in bits is 8 x length of mystr
                                len(bs_hello_str) * 8,
                                data=bs_hello_str,
                                source=self.id,
                                dest=0,
                                packet_type=1
                                )

        # discovery period
        # set a time to wait before broadcasting a new packet
        yield self.timeout(5)
        self.node_status(status=NodeMessages.DISCOVERY_START)
        # send a discovery pdu
        self.phy.send_pdu(discovery_pdu)
        # before we end the discovery period, wait 5 secs
        yield self.timeout(5)
        # discovery period closed

        # schedule devices by allocating a slot to each
        # slot duration = 100 milliseconds
        slot_duration = self.device_counter * .1
        # create a dissemination PDU
        sched_str = NodeMessages.SCHED
        dissemination_pdu = wsp.PDU(None,
                                    # Size in bits is 8 x length of mystr
                                    len(sched_str) * 8,
                                    data=sched_str,
                                    source=self.id,
                                    dest=0,
                                    packet_type=1,
                                    num_devices=self.device_counter,  # number of devices discovered
                                    dev_slots=self.dev_slots,  # list of(device - id, slot number), where slot number
                                    # starts at 0
                                    start_delay=slot_duration,  # delay before communication can begin.
                                    )

        self.display_device_slots(device_slots=self.dev_slots)
        # send dissemination pdu
        self.phy.send_pdu(dissemination_pdu)

        # data period starting
        yield self.timeout(self.device_counter*.1)
        self.node_status(status=NodeMessages.DATA_PERIOD)
