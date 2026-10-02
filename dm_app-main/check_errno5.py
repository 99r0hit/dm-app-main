#!/usr/bin/env python3
import subprocess

print("=== USB Topology (lsusb -t) ===")
subprocess.run(["lsusb", "-t"])

print("\n=== Recent Kernel Dmesg (last 30 lines) ===")
subprocess.run("dmesg -T | tail -n 30", shell=True)

print("\n=== Available /dev/ttyUSB* ports right now ===")
subprocess.run("ls -l /dev/ttyUSB*", shell=True)
