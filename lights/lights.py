#!/usr/bin/env python3
# NeoPixel library strandtest example for rpi_ws281x
import time
from rpi_ws281x import Adafruit_NeoPixel, Color
import argparse
import ast

# LED strip configuration
LED_COUNT = 80     # Number of LED pixels
LED_PIN = 19        # GPIO pin (18 uses PWM)
LED_FREQ_HZ = 800000  # LED signal frequency in hertz
LED_DMA = 10        # DMA channel
LED_BRIGHTNESS = 250 # 0-255 (default, overridden by --brightness)
LED_INVERT = False  # True to invert the signal
LED_CHANNEL = 1     # Set to '1' for GPIOs 13, 19, 41, 45 or 53

# Define functions which animate LEDs in various ways
def colorWipe(strip, color, wait_ms=50):
    """Wipe color across display a pixel at a time."""
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, color)
        strip.show()
        time.sleep(wait_ms / 1000.0)

def solidColor(strip, color, wait_ms=5000):
    """Set all pixels to a solid color."""
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
            return min(curr + step, targ)
        elif curr > targ:
            return max(curr - step, targ)
        return curr
    
    current_rgb = extract_rgb(current_color)
    target_rgb = extract_rgb(target_color)
    
    new_r = adjust_component(current_rgb[0], target_rgb[0], step)
    new_g = adjust_component(current_rgb[1], target_rgb[1], step)
    new_b = adjust_component(current_rgb[2], target_rgb[2], step)
    #print((new_r, new_g, new_b))

    return Color(new_r, new_g, new_b)

def fade(strip, start, end, wait_time=100):
    while start != end:
        start = move_color_closer(start, end)
        solidColor(strip, start, 100)
        #time.sleep(wait_time/1000)

def fade_in(strip, wait_time=10):
    for i in range(255):
        strip.setBrightness(i)
        strip.show()
        time.sleep(wait_time/1000)
    
def fade_out(strip, wait_time=10):
    for i in range(255, 0, -1):
        strip.setBrightness(i)
        strip.show()
        time.sleep(wait_time/1000)
    
# Main program logic
if __name__ == '__main__':
    # Process arguments
    parser = argparse.ArgumentParser(description='Run NeoPixel animations.')
    parser.add_argument('-c', '--clear', action='store_true', help='clear the display on exit')
    parser.add_argument('-p', '--pattern', type=str, help='run a specific pattern, e.g., "solid (255, 255, 0)" or "fade (255, 255, 0) (0, 255, 255)"')
    parser.add_argument('-b', '--brightness', type=int, default=LED_BRIGHTNESS, help='set brightness (0-255)')
    args = parser.parse_args()

    # Validate brightness
    if not (0 <= args.brightness <= 255):
        raise ValueError("Brightness must be between 0 and 255")

    # Create NeoPixel object with specified brightness
    strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, args.brightness, LED_CHANNEL)
    strip.begin()

    # Map pattern names to functions and their default arguments
    pattern_map = {
        'fade-in': (fade_in, None),
        'fade-out': (fade_out, None),
        'solid': (solidColor, None),
        'colorwipe': (colorWipe, None),
        'theaterchase': (theaterChase, Color(127, 127, 127)),
        'rainbow': (rainbow, None),
        'rainbowcycle': (rainbowCycle, None),
        'theaterchaserainbow': (theaterChaseRainbow, None),
        'fade': (fade, [Color(255, 255, 0), Color(0, 255, 255)])
    }

    try:
        if args.pattern:
            # Parse pattern and optional colors
            pattern_parts = args.pattern.lower().split(maxsplit=2)
            pattern_name = pattern_parts[0]
            
            if pattern_name not in pattern_map:
                raise ValueError(f"Unknown pattern: {pattern_name}. Available: {', '.join(pattern_map.keys())}")

            # Handle color parsing
            colors = []
            if len(pattern_parts) > 1:
                try:
                    if pattern_name == 'fade':
                        # Expect two RGB tuples for fade
                        if len(pattern_parts) != 3:
                            raise ValueError("Fade pattern requires two RGB tuples, e.g., 'fade (255, 255, 0) (0, 255, 255)'")
                        start_rgb = ast.literal_eval(pattern_parts[1])
                        end_rgb = ast.literal_eval(pattern_parts[2])
                        if not (isinstance(start_rgb, tuple) and len(start_rgb) == 3 and all(isinstance(x, int) and 0 <= x <= 255 for x in start_rgb)):
                            raise ValueError("Start RGB must be a tuple of 3 integers (0-255), e.g., (255, 255, 0)")
                        if not (isinstance(end_rgb, tuple) and len(end_rgb) == 3 and all(isinstance(x, int) and 0 <= x <= 255 for x in end_rgb)):
                            raise ValueError("End RGB must be a tuple of 3 integers (0-255), e.g., (0, 255, 255)")
                        colors = [Color(*start_rgb), Color(*end_rgb)]
                    else:
                        # Expect one RGB tuple for other patterns
                        rgb = ast.literal_eval(pattern_parts[1])
                        if not (isinstance(rgb, tuple) and len(rgb) == 3 and all(isinstance(x, int) and 0 <= x <= 255 for x in rgb)):
                            raise ValueError("RGB must be a tuple of 3 integers (0-255), e.g., (255, 255, 0)")
                        colors = [Color(*rgb)]
                except (ValueError, SyntaxError):
                    raise ValueError("Invalid RGB format. Use: (r, g, b), e.g., (255, 255, 0)")

            print(f"Running pattern: {pattern_name}")
            func, default_args = pattern_map[pattern_name]
            if pattern_name in ('fade-in', 'solid', 'colorwipe', 'theaterchase'):
                color = colors[0] if colors else default_args
                if color is None:
                    raise ValueError(f"Pattern {pattern_name} requires an RGB color, e.g., (255, 255, 0)")
                func(strip, color)
            elif pattern_name == 'fade':
                start, end = colors if colors else default_args
                func(strip, start, end)
            else:
                # Patterns like rainbow don't need colors
                func(strip)
        else:
            print('Press Ctrl-C to quit.')
            if not args.clear:
                print('Use "-c" argument to clear LEDs on exit')
            while True:
                solidColor(strip, Color(0, 255, 255))
                fade_out(strip)
                fade_in(strip)
                #fade(strip, Color(255, 255, 0), Color(0, 255, 255))
                #fade(strip, Color(0, 255, 255), Color(255, 255, 0))
                print('Color wipe animations.')
                solidColor(strip, Color(255, 255, 0))
                colorWipe(strip, Color(255, 0, 0))
                colorWipe(strip, Color(0, 255, 0))
                colorWipe(strip, Color(0, 0, 255))
                print('Theater chase animations.')
                theaterChase(strip, Color(127, 127, 127))
                theaterChase(strip, Color(127, 0, 0))
                theaterChase(strip, Color(0, 0, 127))
                print('Rainbow animations.')
                rainbow(strip)
                rainbowCycle(strip)
                theaterChaseRainbow(strip)

    except KeyboardInterrupt:
        if args.clear:
            colorWipe(strip, Color(0, 0, 0), 10)
    except ValueError as e:
        print(f"Error: {e}")
        if args.clear:
            colorWipe(strip, Color(0, 0, 0), 10)