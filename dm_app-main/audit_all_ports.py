#!/usr/bin/env python3
import glob
import os
import serial
import time
import serial.tools.list_ports

def audit():
    print("=======================================================")
    print("       DriveMatrix Complete Serial Port Audit")
    print("=======================================================")

    ports = sorted(glob.glob("/dev/ttyUSB*") + glob.glob("/dev/ttyACM*"))
    print(f"Total serial ports found: {len(ports)}\n")

    for p in ports:
        print("-------------------------------------------------------")
        print(f"PORT: {p}")
        
        # Hardware sysfs details
        dev_name = os.path.basename(p)
        sysfs_path = f"/sys/class/tty/{dev_name}/device"
        if os.path.exists(sysfs_path):
            real = os.path.realpath(sysfs_path)
            print(f"  Sysfs Path: {real}")

        # USB VID/PID and Manufacturer
        for info in serial.tools.list_ports.comports():
            if info.device == p:
                vid = f"{info.vid:04x}" if info.vid else "None"
                pid = f"{info.pid:04x}" if info.pid else "None"
                print(f"  USB ID    : {vid}:{pid}")
                print(f"  Mfr       : {info.manufacturer}")
                print(f"  Product   : {info.product}")
                print(f"  Serial    : {info.serial_number}")
                break

        # Probe communication
        try:
            s = serial.Serial(p, 115200, timeout=1.0)
            s.dtr = False
            s.rts = False
            time.sleep(0.05)

            # Trigger reset
            s.rts = True
            time.sleep(0.12)
            s.rts = False

            # Collect startup banner
            start = time.time()
            buf = bytearray()
            while time.time() - start < 1.5:
                if s.in_waiting:
                    buf.extend(s.read(s.in_waiting))
                time.sleep(0.05)

            # If silent, send WHO command (Nano Radio protocol)
            if not buf:
                s.write(b"WHO\n")
                s.flush()
                time.sleep(0.3)
                if s.in_waiting:
                    buf.extend(s.read(s.in_waiting))

            text = buf.decode("utf-8", errors="replace").strip()

            if "rst:0x" in text or "SPI_FAST_FLASH_BOOT" in text:
                print("  ==> IDENTIFIED: [ ESP32 CONTROLLER (Remote Injection) ]")
                first_lines = text.splitlines()[:3]
                print(f"      Banner    : {' | '.join(first_lines)}")
            elif "RADIO_ID:" in text or "DriveMatrix Nano Radio" in text:
                radio_line = [l.strip() for l in text.splitlines() if "RADIO_ID:" in l]
                veh_line = [l.strip() for l in text.splitlines() if "VEHICLE:" in l or "Vehicle:" in l]
                print("  ==> IDENTIFIED: [ ARDUINO NANO RF RADIO ]")
                print(f"      Radio ID  : {radio_line[0] if radio_line else 'Unknown'}")
                print(f"      Vehicle   : {veh_line[0] if veh_line else 'Unknown'}")
            else:
                print("  ==> IDENTIFIED: [ OTHER / SILENT ]")
                if text:
                    print(f"      Output    : {text[:100]}")
                else:
                    print("      Output    : (silent)")

            s.close()
        except Exception as e:
            print(f"  ❌ Error opening port: {e}")

    print("-------------------------------------------------------")
    print("Audit finished.\n")

if __name__ == "__main__":
    audit()
