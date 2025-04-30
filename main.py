import random
import wsnsimpy.wsnsimpy as wsp
from enum import Enum


class Messages(str, Enum):
    HELLO = "HELLO"
    BSHELLO = "BS-HELLO"
    DEVHELLO = "DEV-HELLO"
    SCHED = "SCHED"
    DATA = "DATA"


CONST_TX_RANGE = 150


class BroadcasterNode(wsp.Node):
    def __init__(self, sim, id, pos):
        super().__init__(sim, id, pos)
        self.phy = wsp.DefaultPhyLayer(self)
        self.mac = self  # node object will act as a MAC layer
        self.tx_range = CONST_TX_RANGE
        self.logging = True
        self.devices = []
        self.T1 = 5  # Initial wait and phase timeout
        self.T2 = 0.1  # ACK timeout

    def discovery_phase(self):
        # Create a message to send
        self.log("Discovery starts")
        pdu = wsp.PDU(
            None,  # Bypass MAC layer completely. Since this is scheduled TDMA
            len(Messages.BSHELLO.value) * 8,  # Size in bits
            data=Messages.BSHELLO.value,  # Our message
            source=self.id,  # Source node ID
            dest=wsp.BROADCAST_ADDR,
            type=Messages.BSHELLO.value,
        )
        self.send_pdu(pdu)  # Send immediately

    def scheduling_phase(self):
        # Scheduling Phase
        schedule = {
            "num_devices": len(self.devices),
            "dev_slots": [(dev, idx) for idx, dev in enumerate(self.devices)],
            "start_delay": 1.0,  # delay before data phase
        }
        pdu = wsp.PDU(
            None,  # No MAC layer in this lab
            len(Messages.SCHED.value) * 8,  # Size in bits
            data=Messages.SCHED.value,  # Our message
            source=self.id,  # Source node ID
            dest=wsp.BROADCAST_ADDR,
            type=Messages.SCHED.value,
            payload=schedule,
        )
        self.send_pdu(pdu)
        self.log(f"Schedule: {schedule.get('dev_slots')}")

    def on_receive_pdu(self, pdu):
        # Check if message is DEV-HELLO
        if pdu.type == Messages.DEVHELLO.value:
            if pdu.source not in self.devices:
                self.devices.append(pdu.source)
                self.log(f"Received PDU from {pdu.source}: {pdu.type}")

        # Check if message is DATA
        if pdu.type == Messages.DATA.value:
            self.log("Data period starting")
            self.log(f"Received PDU from {pdu.source}: {pdu.type}")

    def send_pdu(self, pdu):
        # self.log(f"Sent PDU with N={pdu.N}")
        self.phy.send_pdu(pdu)

    def run(self):
        # 5s after boot: start discovery phase (send BS-HELLO)
        self.sim.delayed_exec(self.T1, self.discovery_phase)
        # 10s after boot: end discovery phase and broadcast schedule
        self.sim.delayed_exec(self.T1 + 5, self.scheduling_phase)


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


sim = wsp.Simulator(until=50, timescale=1)

# Create nodes with proper configuration
bs_node = sim.add_node(BroadcasterNode, (random.random() * 100, random.random() * 100))

for x in range(100):
    r_node = sim.add_node(ReceiverNode, (random.random() * 100, random.random() * 100))

sim.run()

# After simulation ends, print PHY stats for each node
print("\n=== Basestation Statistics ===\n")
print(f"  Total TX: {bs_node.phy.stat.total_tx}")
print(f"  Total RX: {bs_node.phy.stat.total_rx}")
print(f"Collisions: {bs_node.phy.stat.total_collision}")
