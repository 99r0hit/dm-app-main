#!/usr/bin/env python3
import serial
import time

def test_bronco2():
    print("=======================================================")
    print("       Direct Radio Test for Bronco 2 (RF-A38DA7)")
    print("=======================================================")
    
    port = "/dev/ttyUSB4"
    print(f"Connecting to {port} at 115200 baud...")
    
    try:
        s = serial.Serial(port, 115200, timeout=1.0)
        time.sleep(0.5)
        
        # Flush buffers
        s.reset_input_buffer()
        s.reset_output_buffer()
        
        # 1. Ask identity & status
        print("\n[1] Querying Radio Identity...")
        s.write(b"WHO\n")
        s.flush()
        time.sleep(0.2)
        while s.in_waiting:
            print("  Nano response:", s.readline().decode('utf-8', errors='replace').strip())
            
        print("\n[2] Querying Pairing / Status...")
        s.write(b"STATUS\n")
        s.flush()
        time.sleep(0.2)
        while s.in_waiting:
            print("  Nano status:", s.readline().decode('utf-8', errors='replace').strip())

        # 2. Send SESSION_START
        print("\n[3] Sending SESSION_START,60...")
        s.write(b"SESSION_START,60\n")
        s.flush()
        time.sleep(0.3)
        while s.in_waiting:
            print("  Session reply:", s.readline().decode('utf-8', errors='replace').strip())

        # 3. Test Steering Sweep
        print("\n[4] Sending Steering Sweep...")
        print("  -> Steer FULL LEFT (CONTROL,-1000,0)...")
        for _ in range(15):
            s.write(b"CONTROL,-1000,0\n")
            s.flush()
            time.sleep(0.08)
            while s.in_waiting:
                print("     RF reply:", s.readline().decode('utf-8', errors='replace').strip())

        time.sleep(0.5)

        print("  -> Steer FULL RIGHT (CONTROL,1000,0)...")
        for _ in range(15):
            s.write(b"CONTROL,1000,0\n")
            s.flush()
            time.sleep(0.08)
            while s.in_waiting:
                print("     RF reply:", s.readline().decode('utf-8', errors='replace').strip())

        time.sleep(0.5)

        print("  -> Steer CENTER (CONTROL,0,0)...")
        for _ in range(5):
            s.write(b"CONTROL,0,0\n")
            s.flush()
            time.sleep(0.08)
            while s.in_waiting:
                print("     RF reply:", s.readline().decode('utf-8', errors='replace').strip())

        # 4. Stop session
        s.write(b"SESSION_STOP\n")
        s.flush()
        time.sleep(0.2)
        while s.in_waiting:
            print("  Stop reply:", s.readline().decode('utf-8', errors='replace').strip())

        s.close()
        print("\nTest completed.")

    except Exception as e:
        print(f"❌ Error testing Bronco 2: {e}")

if __name__ == "__main__":
    test_bronco2()
