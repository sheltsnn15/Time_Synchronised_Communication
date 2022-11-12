# @author Shelton Ngwenya, R00203947

class NodeMessages:  # enum class, has all possible node messages
    WAITING_HELLO = "Waiting for HELLO"
    RECEIVED_PDU_FROM = "Received PDU from"
    BS_HELLO = "BS-HELLO"
    DEV_HELLO = "DEV-HELLO"
    SCHED = "SCHED"
    DATA = "DATA"
    DATA_PERIOD = "Data period starting"
    HAS_SLOT = "Transmitting in slot"
    NO_SLOT = "Didn't get a slot :("
    DISCOVERY_START = "Discovery starts"
