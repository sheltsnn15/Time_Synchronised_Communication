import wsnsimpy.wsnsimpy as wsp

from node_messages import Messages

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
