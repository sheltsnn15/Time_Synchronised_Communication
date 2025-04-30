import random
import wsnsimpy.wsnsimpy as wsp

from node_messages import Messages

CONST_TX_RANGE = 150


class ReceiverNode(wsp.Node):

    def __init__(self, sim, id, pos):
        super().__init__(sim, id, pos)
        self.phy = wsp.DefaultPhyLayer(self)
        self.mac = self  # node object will act as a MAC layer
        self.logging = True
        self.tx_range = CONST_TX_RANGE
        self.bs_id = None  # Track BS ID dynamically
        self.my_slot = None  # Device slot
        self.scheduled = False  # Device slot
        self.next_transmission = None
        self.T1 = 5  # Initial wait and Discovery phase
        self.T2 = 0.1  # ACK timeout

    def discovery_phase(self, source):
        # Create the PDU
        pdu = wsp.PDU(
            None,
            len(Messages.DEVHELLO.value) * 8,  # Size in bits
            source=self.id,
            dest=source,  # ID of base station learned from BS-HELLO
            type=Messages.DEVHELLO.value,
        )
        self.sim.delayed_exec(random.random() * 0.099, self.send_pdu, pdu)

    def scheduling_phase(self, pdu):
        start_delay = pdu.payload.get("start_delay")
        num_devices = pdu.payload.get("num_devices")
        dev_slots = pdu.payload.get("dev_slots")
        self.my_slot = next((idx for dev, idx in dev_slots if dev == self.id), None)
        self.scheduled = self.my_slot is not None
        if self.scheduled:
            my_schedule = start_delay + (self.my_slot * self.T2)
            self.next_transmission = num_devices * self.T2
            self.sim.delayed_exec(my_schedule, self.transmit_data)
        else:
            self.log("Didn't get a slot :(")

    def transmit_data(self):
        pdu = wsp.PDU(
            None,
            len(Messages.DATA.value) * 8,  # Size in bits
            data=Messages.DATA.value,
            source=self.id,
            dest=self.bs_id,
            type=Messages.DATA.value,
        )
        self.send_pdu(pdu)

        # Schedule next transmission
        self.sim.delayed_exec(self.next_transmission, self.transmit_data)

    def on_receive_pdu(self, pdu):
        # Discovery phase
        if pdu.type == Messages.BSHELLO.value:
            self.log(f"Received PDU from {pdu.source}: {pdu.type}")
            self.bs_id = pdu.source  # Store BS ID FIRST
            self.discovery_phase(pdu.source)

        # Scheduling phase
        if pdu.type == Messages.SCHED.value:
            self.log(f"Received PDU from {pdu.source}: {pdu.type}")
            self.scheduling_phase(pdu)
            self.log(f"Transmitting in slot {self.my_slot}")

    def send_pdu(self, pdu):
        self.phy.send_pdu(pdu)

    def run(self):
        self.log("Waiting for HELLO")
