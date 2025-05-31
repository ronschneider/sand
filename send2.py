import serial
import time
import sys
import os

# GRBL settings
SERIAL_PORT = '/dev/ttyACM0'  # Adjust if needed (e.g., '/dev/ttyUSB0')
BAUD_RATE = 115200
TIMEOUT = 120  # Increased timeout for stability

def read_gcode_file(file_path):
    """Read G-code from file and return list of commands."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"G-code file '{file_path}' not found")
    with open(file_path, 'r') as f:
        # Strip whitespace, comments, and empty lines
        commands = [line.strip() for line in f if line.strip() and not line.startswith((';', '('))]
    return commands

def wait_for_grbl(ser, timeout=50):
    """Wait for GRBL to respond with startup message."""
    start_time = time.time()
    ser.flushInput()
    while time.time() - start_time < timeout:
        line = ser.readline().decode().strip()
        print('line = ', line)
        if 'Grbl' in line or 'ok' in line:
            print(f"GRBL ready: {line}")
            return True
        elif line:
            print(f"GRBL response: {line}")
    raise TimeoutError("GRBL did not respond within timeout")

def initialize_grbl(ser, timeout=5):
    """Initialize GRBL with soft reset and wait for startup message."""
    ser.flushInput()
    ser.flushOutput()
    print("Sending soft reset...")
    ser.write(b'\x18')  # Soft reset
    time.sleep(0.5)  # Wait for reset to process

    # Read startup message
    start_time = time.time()
    while time.time() - start_time < timeout:
        line = ser.readline().decode().strip()
        if 'Grbl' in line:
            print(f"GRBL initialized: {line}")
            return True
        elif line:
            print(f"Unexpected response: {line}")
        time.sleep(0.1)  # Avoid tight loop
    print("No GRBL startup message received")
    return False

def send_gcode(commands):
    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=TIMEOUT)
        time.sleep(2)  # Wait for serial connection
        print(f"Connected to GRBL on {SERIAL_PORT}")

        # Initialize GRBL
        if not initialize_grbl(ser):
            raise RuntimeError("Failed to initialize GRBL")

        # Wake up GRBL
        ser.write(b'\r\n\r\n')
        time.sleep(0.2)
        ser.flushInput()

        # Query GRBL status
        ser.write(b'?')
        time.sleep(0.1)
        status = ser.readline().decode().strip()
        print(f"GRBL status: {status}")

        for i, cmd in enumerate(commands, 1):
            cmd = cmd.strip()
            if not cmd:
                continue

            print(f"[{i}/{len(commands)}] Sending: {cmd}")
            ser.write((cmd + '\n').encode())

            # Wait for response with extended timeout for long moves
            start_time = time.time()
            response = ''
            while time.time() - start_time < TIMEOUT:  # 10 seconds for long moves
                response = ser.readline().decode().strip()
                if response:
                    break
                time.sleep(0.1)  # Avoid tight loop
            print(f"-> Response: {response}")

            if response == 'ok':
                pass
            elif 'error' in response.lower():
                print(f"GRBL error: {response}")
                break
            elif response == '':
                print("No response from GRBL, possible timeout")
                break
            else:
                print(f"Unexpected response: {response}")

        print("G-code transmission complete")
        ser.close()
    except serial.SerialException as e:
        print(f"Serial error: {e}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if 'ser' in locals() and ser.is_open:
            ser.close()

def main():
    if len(sys.argv) != 2:
        print("Usage: python3 send_gcode.py <gcode_file>")
        sys.exit(1)

    gcode_file = sys.argv[1]
    try:
        commands = read_gcode_file(gcode_file)
        print(f"Loaded {len(commands)} G-code commands from {gcode_file}")
        send_gcode(commands)
    except FileNotFoundError as e:
        print(e)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
