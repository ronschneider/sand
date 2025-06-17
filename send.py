import serial
import time
import sys
import os
import argparse

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

def send_gcode(commands, ser):
    """Send G-code commands to GRBL."""
    for i, cmd in enumerate(commands, 1):
        cmd = cmd.strip()
        if not cmd:
            continue

        print(f"[{i}/{len(commands)}] Sending: {cmd}")
        ser.write((cmd + '\n').encode())

        # Wait for response with extended timeout for long moves
        start_time = time.time()
        response = ''
        while time.time() - start_time < TIMEOUT:
            response = ser.readline().decode().strip()
            if response:
                break
            time.sleep(0.1)  # Avoid tight loop
        print(f"-> Response: {response}")

        if response == 'ok':
            pass
        elif 'error' in response.lower():
            print(f"GRBL error: {response}")
            return False
        elif response == '':
            print("No response from GRBL, possible timeout")
            return False
        else:
            print(f"Unexpected response: {response}")
    return True

def send_files(preamble_file, gcode_files):
    """Send preamble and G-code files to GRBL."""
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

        # Load preamble commands if provided
        preamble_commands = read_gcode_file(preamble_file) if preamble_file else []

        for gcode_file in gcode_files:  # Corrected line
            try:
                # Send preamble if provided
                if preamble_commands:
                    print(f"\nSending preamble: {preamble_file}")
                    if not send_gcode(preamble_commands, ser):
                        print(f"Failed to send preamble for {gcode_file}")
                        continue

                # Send G-code file
                print(f"\nSending G-code file: {gcode_file}")
                commands = read_gcode_file(gcode_file)
                print(f"Loaded {len(commands)} G-code commands from {gcode_file}")
                if not send_gcode(commands, ser):
                    print(f"Failed to send {gcode_file}")
                    continue
            except FileNotFoundError as e:
                print(e)
                continue

        print("All G-code transmissions complete")
        ser.close()
    except serial.SerialException as e:
        print(f"Serial error: {e}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if 'ser' in locals() and ser.is_open:
            ser.close()

def main():
    parser = argparse.ArgumentParser(description="Send G-code files to GRBL with optional preamble")
    parser.add_argument('--preamble', type=str, help="Path to preamble G-code file")
    parser.add_argument('gcode_files', nargs='+', help="Path(s) to G-code file(s)")
    args = parser.parse_args()

    if not args.gcode_files:
        print("Error: At least one G-code file must be provided")
        sys.exit(1)

    # Verify preamble file exists if provided
    if args.preamble and not os.path.exists(args.preamble):
        print(f"Error: Preamble file '{args.preamble}' not found")
        sys.exit(1)

    send_files(args.preamble, args.gcode_files)

if __name__ == "__main__":
    main()
