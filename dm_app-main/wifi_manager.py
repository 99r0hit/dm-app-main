import time
import subprocess

AP_SSID = "DriveMatrix-AP"
AP_PASSWORD = "drivematrix"


def _wifi_devices():
    """Return [(device, active_connection_name)] for every Wi-Fi NIC."""
    try:
        output = subprocess.check_output(
            ["nmcli", "-t", "-f", "DEVICE,TYPE,CONNECTION", "device", "status"]
        ).decode()
    except Exception as e:
        print(f"[WiFi Manager] Device list error: {e}", flush=True)
        return []

    devices = []
    for line in output.splitlines():
        parts = line.split(":")
        if len(parts) >= 3 and parts[1] == "wifi":
            devices.append((parts[0], parts[2]))
    return devices


def get_dongle_interface():
    """Return the client USB Wi-Fi dongle interface.

    wlan0 (onboard) is reserved for the DriveMatrix-AP hotspot and must
    never be repurposed to join an external network, so it is always
    excluded here.
    """
    for device, connection in _wifi_devices():
        if device == "wlan0" or connection == AP_SSID:
            continue
        return device
    return None


def get_dongle_connection_name():
    """Return the SSID currently active on the dongle interface, if any."""
    interface = get_dongle_interface()
    if not interface:
        return None

    for device, connection in _wifi_devices():
        if device == interface and connection and connection != "--":
            return connection
    return None


def scan_networks():
    interface = get_dongle_interface()
    if not interface:
        print("[WiFi Manager] No USB Wi-Fi dongle detected for scanning", flush=True)
        return []

    try:
        result = subprocess.check_output([
            "nmcli",
            "-t",
            "-f",
            "SSID,SIGNAL",
            "device",
            "wifi",
            "list",
            "ifname",
            interface,
            "--rescan",
            "yes"
        ]).decode()

        networks = {}

        for line in result.splitlines():
            try:
                parts = line.split(":")
                if len(parts) >= 2:
                    ssid = parts[0].strip()
                    signal = parts[1].strip()
                    if ssid:
                        sig_int = int(signal) if signal.isdigit() else 0
                        if ssid not in networks:
                            networks[ssid] = sig_int
                        else:
                            networks[ssid] = max(networks[ssid], sig_int)
            except Exception:
                pass

        return sorted(
            networks.items(),
            key=lambda x: x[1],
            reverse=True
        )
    except Exception as e:
        print(f"[WiFi Manager] Scan error: {e}", flush=True)
        return []

def connect_wifi(ssid, password=""):
    """Connect the USB dongle interface to an external Wi-Fi network.

    wlan0's DriveMatrix-AP hotspot is never touched by this call.
    """
    ssid = (ssid or "").strip()
    if not ssid:
        return False, "No network selected"

    interface = get_dongle_interface()
    if not interface:
        return False, "No USB Wi-Fi dongle detected"

    command = [
        "sudo", "nmcli", "device", "wifi", "connect", ssid,
        "ifname", interface
    ]
    if password:
        command += ["password", password]

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode != 0:
            error = (result.stderr or result.stdout or "Connection failed").strip()
            print(f"[WiFi Manager] Connect failed: {error}", flush=True)
            return False, error

        print(f"[WiFi Manager] Dongle {interface} connected to {ssid}", flush=True)
        return True, None
    except Exception as e:
        print(f"[WiFi Manager] Connect error: {e}", flush=True)
        return False, str(e)

def get_wifi_state():
    try:
        output = subprocess.check_output(
            ["nmcli", "-t", "-f", "TYPE,STATE,CONNECTION", "device"]
        ).decode().splitlines()
        
        for line in output:
            parts = line.split(":")
            if len(parts) >= 2 and parts[0] == "wifi":
                state = parts[1]
                conn_name = parts[2] if len(parts) > 2 else ""
                return state, conn_name
    except Exception:
        pass
    return "disconnected", ""

def start_access_point():
    print("[WiFi Manager] Starting Access Point...", flush=True)
    try:
        connections = subprocess.check_output(
            ["nmcli", "-t", "-f", "NAME", "connection", "show"]
        ).decode().splitlines()

        if AP_SSID in connections:
            subprocess.call(["sudo", "nmcli", "connection", "up", AP_SSID])
        else:
            subprocess.call([
                "sudo", "nmcli", "device", "wifi", "hotspot",
                "ifname", "wlan0",
                "ssid", AP_SSID,
                "password", AP_PASSWORD
            ])
            subprocess.call([
                "sudo", "nmcli", "connection", "modify",
                "Hotspot", "connection.id", AP_SSID
            ])
    except Exception as e:
        print(f"[WiFi Manager] Failed to start AP: {e}", flush=True)

def monitor_wifi():
    time.sleep(10)

    # Start DriveMatrix AP once if it is not already active.
    state, conn_name = get_wifi_state()

    if conn_name != AP_SSID:
        print(
            f"[WiFi Manager] Starting {AP_SSID} "
            f"(current connection: {conn_name or 'NONE'})",
            flush=True
        )
        start_access_point()

    # Keep the process alive.
    # Do NOT force DriveMatrix-AP back if the user manually
    # changes Wi-Fi using nmcli.
    while True:
        time.sleep(60)

if __name__ == "__main__":
    monitor_wifi()
