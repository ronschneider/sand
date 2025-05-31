#!/usr/bin/env python3
# NeoPixel library strandtest example for rpi_ws281x
import time
from rpi_ws281x import Adafruit_NeoPixel, Color
import argparse

# LED strip configuration
LED_COUNT = 80     # Number of LED pixels
LED_PIN = 19        # GPIO pin (18 uses PWM)
LED_FREQ_HZ = 800000  # LED signal frequency in hertz
LED_DMA = 10        # DMA channel
LED_BRIGHTNESS = 250 # 0-255
LED_INVERT = False  # True to invert the signal
LED_CHANNEL = 1     # Set to '1' for GPIOs 13, 19, 41, 45 or 53

# Define functions which animate LEDs in various ways
def colorWipe(strip, color, wait_ms=50):
    """Wipe color across display a pixel at a time."""
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, color)
        strip.show()
        time.sleep(wait_ms / 1000.0)

# Define functions which animate LEDs in various ways
def solidColor(strip, color, wait_ms=5000):
    """Wipe color across display a pixel at a time."""
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, color)
        strip.show()
    time.sleep(wait_ms / 1000.0)

def theaterChase(strip, color, wait_ms=50, iterations=10):
    """Movie theater light style chaser animation."""
    for j in range(iterations):
        for q in range(3):
            for i in range(0, strip.numPixels(), 3):
                strip.setPixelColor(i + q, color)
            strip.show()
            time.sleep(wait_ms / 1000.0)
            for i in range(0, strip.numPixels(), 3):
                strip.setPixelColor(i + q, 0)

def wheel(pos):
    """Generate rainbow colors across 0-255 positions."""
    if pos < 85:
        return Color(pos * 3, 255 - pos * 3, 0)
    elif pos < 170:
        pos -= 85
        return Color(255 - pos * 3, 0, pos * 3)
    else:
        pos -= 170
        return Color(0, pos * 3, 255 - pos * 3)

def rainbow(strip, wait_ms=20, iterations=1):
    """Draw rainbow that fades across all pixels at once."""
    for j in range(256 * iterations):
        for i in range(strip.numPixels()):
            strip.setPixelColor(i, wheel((i + j) & 255))
        strip.show()
        time.sleep(wait_ms / 1000.0)

def rainbowCycle(strip, wait_ms=20, iterations=5):
    """Draw rainbow that uniformly distributes itself across all pixels."""
    for j in range(256 * iterations):
        for i in range(strip.numPixels()):
            strip.setPixelColor(i, wheel((int(i * 256 / strip.numPixels()) + j) & 255))
        strip.show()
        time.sleep(wait_ms / 1000.0)

def theaterChaseRainbow(strip, wait_ms=50):
    """Rainbow movie theater light style chaser animation."""
    for j in range(256):
        for q in range(3):
            for i in range(0, strip.numPixels(), 3):
                strip.setPixelColor(i + q, wheel((i + j) % 255))
            strip.show()
            time.sleep(wait_ms / 1000.0)
            for i in range(0, strip.numPixels(), 3):
                strip.setPixelColor(i + q, 0)

def extract_rgb(color: Color) -> tuple:
    return ((color >> 16) & 0xFF, (color >> 8) & 0xFF, color & 0xFF)

def move_color_closer(current_color: Color, target_color: Color, step: int = 1) -> Color:
    def adjust_component(curr: int, targ: int, step: int) -> int:
        if curr < targ:
            return min(curr + step, targ)  # Move up, don't overshoot
        elif curr > targ:
            return max(curr - step, targ)  # Move down, don't overshoot
        return curr
    
    # Extract RGB values from Color objects
    current_rgb = extract_rgb(current_color)
    target_rgb = extract_rgb(target_color)
    
    # Adjust each component
    new_r = adjust_component(current_rgb[0], target_rgb[0], step)
    new_g = adjust_component(current_rgb[1], target_rgb[1], step)
    new_b = adjust_component(current_rgb[2], target_rgb[2], step)
    
    # Return new Color object
    return Color(new_r, new_g, new_b)

def fade(strip, start, end, wait_time=100):
    while start != end:
        start = move_color_closer(start, end)
        solidColor(strip, start, 0)
        time.sleep(wait_time/1000)

# Main program logic
if __name__ == '__main__':
    # Process arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--clear', action='store_true', help='clear the display on exit')
    args = parser.parse_args()

    # Create NeoPixel object
    strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
    strip.begin()

    print('Press Ctrl-C to quit.')
    if not args.clear:
        print('Use "-c" argument to clear LEDs on exit')

    try:
        while True:
            fade(strip, Color(255, 255, 0), Color(0, 255, 255))
            fade(strip, Color(0, 255, 255), Color(255, 255, 0))

            print('Color wipe animations.')
            solidColor(strip, Color(255, 255,0))  # Red wipe
            colorWipe(strip, Color(255, 0, 0))  # Red wipe
            colorWipe(strip, Color(0, 255, 0))  # Green wipe
            colorWipe(strip, Color(0, 0, 255))  # Blue wipe
            print('Theater chase animations.')
            theaterChase(strip, Color(127, 127, 127))  # White
            theaterChase(strip, Color(127, 0, 0))  # Red
            theaterChase(strip, Color(0, 0, 127))  # Blue
            print('Rainbow animations.')
            rainbow(strip)
            rainbowCycle(strip)
            theaterChaseRainbow(strip)

    except KeyboardInterrupt:
        if args.clear:
            colorWipe(strip, Color(0, 0, 0), 10)