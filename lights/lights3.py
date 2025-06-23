

#!/usr/bin/env python3
# NeoPixel strandtest example converted for Pi5Neo library
import time
from pi5neo import Pi5Neo
import argparse

# LED strip configuration
LED_COUNT = 80      # Number of LED pixels
LED_BRIGHTNESS = 250  # 0-255 (will be converted to 0-1 for Pi5Neo)
LED_BRIGHTNESS_FLOAT = LED_BRIGHTNESS / 255.0  # Convert to 0-1 scale

# Define functions which animate LEDs in various ways
def colorWipe(strip, color, wait_ms=50):
    """Wipe color across display a pixel at a time."""
    for i in range(LED_COUNT):
        strip.set_pixel(i, color)  # color is an RGB tuple (r, g, b)
        strip.show()
        time.sleep(wait_ms / 1000.0)

def solidColor(strip, color, wait_ms=5000):
    """Set all pixels to a solid color."""
    for i in range(LED_COUNT):
        strip.set_led_color(i, color)
    strip.show()
    time.sleep(wait_ms / 1000.0)

def theaterChase(strip, color, wait_ms=50, iterations=10):
    """Movie theater light style chaser animation."""
    for j in range(iterations):
        for q in range(3):
            for i in range(0, LED_COUNT, 3):
                strip.set_pixel(i + q, color)
            strip.show()
            time.sleep(wait_ms / 1000.0)
            for i in range(0, LED_COUNT, 3):
                strip.set_pixel(i + q, (0, 0, 0))  # Turn off

def wheel(pos):
    """Generate rainbow colors across 0-255 positions, return RGB tuple."""
    if pos < 85:
        return (pos * 3, 255 - pos * 3, 0)
    elif pos < 170:
        pos -= 85
        return (255 - pos * 3, 0, pos * 3)
    else:
        pos -= 170
        return (0, pos * 3, 255 - pos * 3)

def rainbow(strip, wait_ms=20, iterations=1):
    """Draw rainbow that fades across all pixels at once."""
    for j in range(256 * iterations):
        for i in range(LED_COUNT):
            strip.set_pixel(i, wheel((i + j) & 255))
        strip.show()
        time.sleep(wait_ms / 1000.0)

def rainbowCycle(strip, wait_ms=20, iterations=5):
    """Draw rainbow that uniformly distributes itself across all pixels."""
    for j in range(256 * iterations):
        for i in range(LED_COUNT):
            strip.set_pixel(i, wheel((int(i * 256 / strip.get_pixel_count()) + j) & 255))
        strip.show()
        time.sleep(wait_ms / 1000.0)

def theaterChaseRainbow(strip, wait_ms=50):
    """Rainbow movie theater light style chaser animation."""
    for j in range(256):
        for q in range(3):
            for i in range(0, LED_COUNT, 3):
                strip.set_pixel(i + q, wheel((i + j) % 255))
            strip.show()
            time.sleep(wait_ms / 1000.0)
            for i in range(0, LED_COUNT, 3):
                strip.set_pixel(i + q, (0, 0, 0))

def extract_rgb(color):
    """Return RGB tuple (already in correct format for Pi5Neo)."""
    return color  # No conversion needed, as color is already (r, g, b)

def move_color_closer(current_color, target_color, step=1):
    """Move current RGB color closer to target RGB color by step."""
    def adjust_component(curr, targ, step):
        if curr < targ:
            return min(curr + step, targ)
        elif curr > targ:
            return max(curr - step, targ)
        return curr

    # Adjust each component
    new_r = adjust_component(current_color[0], target_color[0], step)
    new_g = adjust_component(current_color[1], target_color[1], step)
    new_b = adjust_component(current_color[2], target_color[2], step)

    return (new_r, new_g, new_b)

def fade(strip, start_color, end_color, wait_time=100):
    """Fade from start_color to end_color."""
    current = start_color
    while current != end_color:
        current = move_color_closer(current, end_color)
        solidColor(strip, current, 0)
        time.sleep(wait_time / 1000)

# Main program logic
if __name__ == '__main__':
    # Process arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--clear', action='store_true', help='clear the display on exit')
    args = parser.parse_args()

    # Create NeoPixel object
    strip = Pi5Neo('/dev/spidev0.0',  LED_COUNT, 800) #LED_BRIGHTNESS_FLOAT)  # Brightness as 0-1 float

    print('Press Ctrl-C to quit.')
    if not args.clear:
        print('Use "-c" argument to clear LEDs on exit')

    try:
        while True:
            fade(strip, (255, 255, 0), (0, 255, 255))  # Yellow to Cyan
            fade(strip, (0, 255, 255), (255, 255, 0))  # Cyan to Yellow

            print('Color wipe animations.')
            solidColor(strip, (255, 255, 0))  # Yellow
            colorWipe(strip, (255, 0, 0))    # Red
            colorWipe(strip, (0, 255, 0))    # Green
            colorWipe(strip, (0, 0, 255))    # Blue
            print('Theater chase animations.')
            theaterChase(strip, (127, 127, 127))  # White
            theaterChase(strip, (127, 0, 0))      # Red
            theaterChase(strip, (0, 0, 127))      # Blue
            print('Rainbow animations.')
            rainbow(strip)
            rainbowCycle(strip)
            theaterChaseRainbow(strip)

    except KeyboardInterrupt:
        if args.clear:
            strip.clear()  # Turn off all pixels
            strip.show()

