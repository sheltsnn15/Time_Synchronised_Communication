<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**  *generated with [DocToc](https://github.com/thlorenz/doctoc)*

- [WSNSimPy TDMA-Based Wireless Sensor Network Simulation](#wsnsimpy-tdma-based-wireless-sensor-network-simulation)
  - [Overview](#overview)
  - [Requirements](#requirements)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# WSNSimPy TDMA-Based Wireless Sensor Network Simulation

A simulation of a wireless sensor network using **WSNSimPy**, implementing a basic **TDMA (Time Division Multiple Access)** communication protocol with collision modeling.

## Overview

This simulates a network of one base station (BS) and multiple receiver nodes using a TDMA scheme:

- **Discovery Phase**: BS broadcasts a `BS-HELLO`; devices respond with `DEV-HELLO`.
- **Scheduling Phase**: BS assigns time slots to each device.
- **Data Phase**: Devices transmit `DATA` in assigned slots.

WSNSimPy's physical layer is used to model **range-based transmission** and **collision detection**.

[Sequence_Diagram](./sequence_diagram.png)

## Requirements

- Python 3.8+
- [wsnsimpy](https://github.com/saraHossein/wsn-simpy-)

```bash
pip install wsnsimpy


