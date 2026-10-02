#!/usr/bin/env python3
import glob
import os
import re
import subprocess
import time
import evdev
from evdev import ecodes

G29_NAME = "Logitech G29 Driving Force Racing Wheel"

def get_throttled_status():
    try:
        res = subprocess.run(["vcgencmd", "get_throttled"], capture_output=True, text=True, timeout=1)
        if res.returncode == 0:
            val = res.stdout.strip()
            # 0x0 means normal, anything else indicates undervoltage / throttling
            if "0x0" in val:
                return "Power OK (throttled=0x0)"
            else:
                return f"⚠️ UNDERVOLTAGE / THROTTLING DETECTED ({val})!"
    except Exception:
        pass
    return "Power check unavailable"

def scan_wheels():
    wheels = []
    for path in sorted(glob.glob("/dev/input/event*")):
        try:
            dev = evdev.InputDevice(path)
            if dev.name == G29_NAME:
                wheels.append(dev)
            else:
                dev.close()
        except Exception:
            pass
    return wheels

def test_loop():
    print("=" * 75)
    print("  DriveMatrix - G29 Wheel Plug & Port Mapping Tester")
    print("=" * 75)
    print("Plug in your powered USB hub, then plug wheels in one by one.")
    print("Press Ctrl+C to exit.\n")

    last_count = -1

    while True:
        wheels = scan_wheels()
        pwr = get_throttled_status()
        
        # Clear screen and redraw
        os.system("clear")
        print("=" * 75)
        print("  DriveMatrix - G29 Wheel Plug & Port Mapping Tester")
        print(f"  System Power Status: {pwr}")
        print("=" * 75)
        print(f"Total G29 Wheels Detected: {len(wheels)} / 4\n")

        if not wheels:
            print("  [Waiting] No G29 wheels detected yet...")
            print("  -> Ensure your powered USB hub is plugged into the Pi.")
            print("  -> Plug in a steering wheel and check if the wheel calibrates.\n")
        else:
            print(f"{'Node':<18} | {'Phys Path':<34} | {'Target Cockpit':<18}")
            print("-" * 75)
            port_map = {
                "1.4.1": 1,
                "1.4.2": 2,
                "1.4.3.2": 3,
                "1.4.3.1": 4,
                "1.4.3": 3,
                "1.4.4": 4,
            }

            for idx, w in enumerate(wheels, start=1):
                phys = str(getattr(w, "phys", "") or "").strip()
                assigned_cockpit = None

                match = re.search(r"-([0-9\.]+)/input\d+$", phys)
                if match:
                    chain = match.group(1)
                    for key, num in port_map.items():
                        if chain.endswith(key):
                            assigned_cockpit = num
                            break

                if assigned_cockpit:
                    target = f"✅ Cockpit {assigned_cockpit}"
                else:
                    target = "⚠️ Unmapped"

                ffb_ok = "FFB: OK" if ecodes.EV_FF in w.capabilities() else "FFB: NO"
                print(f"{w.path:<18} | {phys:<34} | {target:<20} [{ffb_ok}]")

            print("\n" + "-" * 75)
            print("  Physical Paths detected for your wheels:")
            for idx, w in enumerate(wheels, start=1):
                phys = str(getattr(w, "phys", "") or "").strip()
                print(f"    Wheel {idx}: {phys}")

        # Close handles to avoid holding open devices
        for w in wheels:
            try:
                w.close()
            except Exception:
                pass

        time.sleep(1.0)

if __name__ == "__main__":
    try:
        test_loop()
    except KeyboardInterrupt:
        print("\nTest stopped.")
