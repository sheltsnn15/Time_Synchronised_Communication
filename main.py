import wsnsimpy.wsnsimpy as wsp
import random

from broadcaster import BroadcasterNode
from devices import ReceiverNode

sim = wsp.Simulator(
    until=50,  # length of simulation (seconds)
    timescale=1,  # 1 is real time, 0 is as fast as possible
)

bs_node = sim.add_node(BroadcasterNode, (random.random() * 100, random.random() * 100))

for x in range(100):
    r_node = sim.add_node(ReceiverNode, (random.random() * 100, random.random() * 100))


if __name__ == "__main__":
    sim.run()
    # After simulation ends, print PHY stats for each node
    print("\n=== Basestation Statistics ===\n")
    print(f"  Total TX: {bs_node.phy.stat.total_tx}")
    print(f"  Total RX: {bs_node.phy.stat.total_rx}")
    print(f"Collisions: {bs_node.phy.stat.total_collision}")
