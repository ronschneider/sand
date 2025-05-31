import serial
import time
import sys
import os

# GRBL settings
SERIAL_PORT = '/dev/ttyACM0'  # Adjust if needed (e.g., '/dev/ttyACM0')
BAUD_RATE = 115200

def read_gcode_file(file_path):
    """Read G-code from file and return list of commands."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"G-code file '{file_path}' not found")
    with open(file_path, 'r') as f:
        # Strip whitespace and comments, ignore empty lines
        commands = [line.strip() for line in f if line.strip() and not line.startswith(';')]
    return commands

def send_gcode(commands):
    """Send G-code commands to GRBL."""
    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        time.sleep(2)  # Wait for GRBL to initialize
        ser.write(b'\x18')  # Soft reset
        ser.readline()  # Wait for GRBL startup message
        print(f"Connected to GRBL on {SERIAL_PORT}")

        # Wake up GRBL
        ser.write(b'\r\n\r\n')
        time.sleep(0.1)
        ser.flushInput()

        for i, cmd in enumerate(commands, 1):
            cmd = cmd.strip()
            if cmd:  # Skip empty commands
                print('sending ', cmd)
                ser.write((cmd + '\n').encode())
                while True:
                    response = ser.readline().decode().strip()
                    print("-> ", response)
                    if response == 'ok':
                        break
                    elif 'error' in response.lower():
                        print(f"GRBL error: {response}")
                        break
                    elif response == '':
                        print('empty response, treading water')
                    else:
                        print('unknown response ', response)

                print(f"[{i}/{len(commands)}] Sent: {cmd}, Response: {response}")
                if 'error' in response.lower():
                    print(f"GRBL error: {response}")
                    break

        ser.close()
        print("G-code sent successfully")
    except serial.SerialException as e:
        print(f"Serial error: {e}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if 'ser' in locals() and ser.is_open:
            ser.close()

def main():
    # Check command-line argument
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