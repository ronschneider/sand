from periphery import SPI
import time

# WS281x settings
LED_COUNT = 30
LED_BRIGHTNESS = 255  # 0-255
SPI_DEVICE = "/dev/spidev0.0"
SPI_SPEED = 8000000  # 8 MHz, suitable for WS281x

# WS281x timing (approximated for SPI)
def ws281x_encode(pixel):
    """Encode RGB pixel for WS281x SPI transmission."""
    r, g, b = pixel
    encoded = []
    for value in (g, r, b):  # GRB order for WS281x
        for i in range(7, -1, -1):
            bit = (value >> i) & 1
            # WS281x uses 3 SPI bits per LED bit (0: 100, 1: 110)
            encoded.extend([0x6 if bit else 0x4])
    return encoded

# Initialize SPI
spi = SPI(SPI_DEVICE, 0, SPI_SPEED)

# Create pixel array (all red)
pixels = [(LED_BRIGHTNESS, 0, 0)] * LED_COUNT
data = []
for pixel in pixels:
    data.extend(ws281x_encode(pixel))

# Send data to LEDs
spi.transfer(bytearray(data))
time.sleep(101)  # Brief pause to ensure data is latched

