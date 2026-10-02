#!/usr/bin/env python3
import serial
import time

def test_sweep(port, name):
    print(f"\n==========================================")
    print(f"  Testing {name} on {port}")
    print(f"==========================================")
    try:
        s = serial.Serial(port, 115200, timeout=1.0)
        
        # 1. Full LEFT Steering (steering = 0, throttle = 124 neutral)
        left_pkt = bytes([0xAA, 124, 0, 124 ^ 0])
        print("  -> Steering FULL LEFT (1.5 seconds)...")
        for _ in range(15):
            s.write(left_pkt)
            s.flush()
            time.sleep(0.1)

        # 2. Full RIGHT Steering (steering = 255, throttle = 124 neutral)
        right_pkt = bytes([0xAA, 124, 255, 124 ^ 255])
        print("  -> Steering FULL RIGHT (1.5 seconds)...")
        for _ in range(15):
            s.write(right_pkt)
            s.flush()
            time.sleep(0.1)

        # 3. Return to CENTER (steering = 128, throttle = 124 neutral)
        center_pkt = bytes([0xAA, 124, 128, 124 ^ 128])
        print("  -> Centering steering...")
        for _ in range(5):
            s.write(center_pkt)
            s.flush()
            time.sleep(0.1)

        s.close()
        print(f"  ✅ {name} test completed!")
    except Exception as e:
        print(f"  ❌ Error on {port}: {e}")

if __name__ == "__main__":
    print("Testing ESP Remote Injection Steering Sweep...")
    # ESP 1 is on /dev/ttyUSB1
    test_sweep("/dev/ttyUSB1", "ESP Car 1")
    time.sleep(1.0)
    # ESP 2 is on /dev/ttyUSB3 (identified via Silicon Labs CP2102)
    test_sweep("/dev/ttyUSB3", "ESP Car 2")
    print("\nSweep test finished! Check if ESP Car 2 steered Left and Right!")
