#!/usr/bin/env python3
import serial
import time
import sys

def diagnose_port(port, name):
    print(f"\n=======================================================")
    print(f"  Diagnosing: {name} on {port}")
    print(f"=======================================================")
    try:
        s = serial.Serial(port, 115200, timeout=0.5)
        # Ensure DTR and RTS are released
        s.dtr = False
        s.rts = False
        time.sleep(0.1)

        # 1. Test Reset & Boot Log
        print("  [1/3] Resetting ESP via RTS/DTR lines...")
        s.rts = True
        time.sleep(0.15)
        s.rts = False
        time.sleep(0.05)

        print("  -> Listening for ESP boot output (1.5 seconds)...")
        start = time.time()
        output = bytearray()
        while time.time() - start < 1.5:
            if s.in_waiting:
                output.extend(s.read(s.in_waiting))
            time.sleep(0.05)

        boot_text = output.decode("utf-8", errors="replace").strip()
        if boot_text:
            print(f"  📥 ESP Boot Output:\n{boot_text}")
        else:
            print("  ⚠️ No boot text received (firmware silent or auto-reset not wired)")

        # 2. Steering Test
        print("\n  [2/3] Sending Steering Commands...")
        # Left
        left_pkt = bytes([0xAA, 124, 0, 124 ^ 0])
        print("     -> Sending FULL LEFT (steering=0)...")
        for _ in range(10):
            s.write(left_pkt)
            s.flush()
            time.sleep(0.05)
        time.sleep(0.5)

        # Right
        right_pkt = bytes([0xAA, 124, 255, 124 ^ 255])
        print("     -> Sending FULL RIGHT (steering=255)...")
        for _ in range(10):
            s.write(right_pkt)
            s.flush()
            time.sleep(0.05)
        time.sleep(0.5)

        # Center
        center_pkt = bytes([0xAA, 124, 128, 124 ^ 128])
        print("     -> Sending CENTER (steering=128)...")
        for _ in range(5):
            s.write(center_pkt)
            s.flush()
            time.sleep(0.05)

        # 3. Throttle Test (Gentle pulse)
        print("\n  [3/3] Sending Throttle Commands (brief pulse)...")
        fwd_pkt = bytes([0xAA, 160, 128, 160 ^ 128])
        print("     -> Sending GENTLE FORWARD (throttle=160)...")
        for _ in range(10):
            s.write(fwd_pkt)
            s.flush()
            time.sleep(0.05)
        time.sleep(0.5)

        # Return to neutral
        neutral_pkt = bytes([0xAA, 124, 128, 124 ^ 128])
        for _ in range(5):
            s.write(neutral_pkt)
            s.flush()
            time.sleep(0.05)

        # Read any incoming serial feedback
        time.sleep(0.2)
        feedback = s.read(s.in_waiting or 0)
        if feedback:
            print(f"  📥 Received serial feedback from ESP: {feedback}")
        else:
            print("  ℹ️ No serial feedback (normal if firmware does not echo)")

        s.close()
        print(f"  ✅ Completed test on {port}")

    except Exception as e:
        print(f"  ❌ Error on {port}: {e}")

if __name__ == "__main__":
    print("=======================================================")
    print("   DriveMatrix ESP Remote Injection Hardware Diagnostic")
    print("=======================================================")
    print("Note: Ensure Car 1 and Car 2 remotes and cars are powered ON.")
    
    diagnose_port("/dev/ttyUSB1", "ESP Car 1 on /dev/ttyUSB1")
    time.sleep(1.0)
    diagnose_port("/dev/ttyUSB3", "ESP Car 2 on /dev/ttyUSB3")
    print("\nDiagnostic complete.\n")
