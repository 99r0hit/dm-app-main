#!/usr/bin/env python3
import serial
import time

print("=" * 60)
print("  DriveMatrix - Direct ESP Port Tester")
print("=" * 60)

for port in ['/dev/ttyUSB1', '/dev/ttyUSB2']:
    print(f"\nTesting {port}...")
    try:
        s = serial.Serial(port, 115200, timeout=1.0)
        # Send an ESP neutral packet: 0xAA, throttle=128, steering=128, checksum=0
        packet = bytes([0xAA, 128, 128, 0])
        s.write(packet)
        s.flush()
        print(f"  ✅ {port}: PACKET SENT SUCCESSFULLY (0xAA 0x80 0x80 0x00)")
        time.sleep(0.2)
        resp = s.read(s.in_waiting or 0)
        if resp:
            print(f"  📥 Received response ({len(resp)} bytes): {resp}")
        else:
            print(f"  ℹ️ (No serial feedback returned by board)")
        s.close()
    except Exception as e:
        print(f"  ❌ {port}: FAILED -> {e}")

print("\n" + "=" * 60)
