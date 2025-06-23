#!/usr/bin/env python3
# NeoPixel animation script using Pi5Neo SPI interface
import time
import argparse
import ast
from pi5neo import Pi5Neo, LEDColor, EPixelType

# LED strip configuration
LED_COUNT = 80        # Number of LED pixels
SPI_DEVICE = '/dev/spidev0.0'  # SPI device (adjust if not using SPI0 CE0)
SPI_SPEED_KHZ = 800   # SPI speed in kHz (matches 800kHz from original)
LED_BRIGHTNESS = 250  # 0-255 (default, overridden by --brightness)
PIXEL_TYPE = EPixelType.RGB  # Set to EPixelType.RGBW for RGBW strips
QUIET_MODE = False    # Set to True to suppress SPI debug messages

def apply_brightness(color, brightness):
    """Scale RGB values based on brightness (0-255)."""
    scale = brightness / 255.0
    return LEDColor(
        red=int(color.red * scale),
        green=int(color.green * scale),
        blue=int(color.blue * scale),
        white=int(color.white * scale)
    )

def colorWipe(neo, color, wait_ms=50):
    """Wipe color across display a pixel at a time."""
    for i in range(neo.num_leds):
        neo.set_led_color(i, color.red, color.green, color.blue, color.white)
        neo.update_strip(wait_ms / 1000.0)

def solidColor(neo, color, wait_ms=5000):
    """Set all pixels to a solid color."""
    neo.fill_strip(color.red, color.green, color.blue, color.white)
    neo.update_strip(wait_ms / 1000.0)

def theaterChase(neo, color, wait_ms=50, iterations=10):
    """Movie theater light style chaser animation."""
    for j in range(iterations):
        for q in range(3):
            for i in range(0, neo.num_leds, 3):
                neo.set_led_color(i + q, color.red, color.green, color.blue, color.white)
            neo.update_strip(wait_ms / 1000.0)
            for i in range(0, neo.num_leds, 3):
                neo.set_led_color(i + q, 0, 0, 0, 0)
            neo.update_strip(0)  # Immediate update to clear

def wheel(pos):
    """Generate rainbow colors across 0-255 positions."""
    if pos < 85:
        return LEDColor(pos * 3, 255 - pos * 3, 0)
    elif pos < 170:
        pos -= 85
        return LEDColor(255 - pos * 3, 0, pos * 3)
    else:
        pos -= 170
        return LEDColor(0, pos * 3, 255 - pos * 3)

def rainbow(neo, wait_ms=20, iterations=1):
    """Draw rainbow that fades across all pixels at once."""
    for j in range(256 * iterations):
        for i in range(neo.num_leds):
            color = wheel((i + j) & 255)
            neo.set_led_color(i, color.red, color.green, color.blue, color.white)
        neo.update_strip(wait_ms / 1000.0)

def rainbowCycle(neo, wait_ms=20, iterations=5):
    """Draw rainbow that uniformly distributes itself across all pixels."""
    for j in range(256 * iterations):
        for i in range(neo.num_leds):
            color = wheel((int(i * 256 / neo.num_leds) + j) & 255)
            neo.set_led_color(i, color.red, color.green, color.blue, color.white)
        neo.update_strip(wait_ms / 1000.0)

def theaterChaseRainbow(neo, wait_ms=50):
    """Rainbow movie theater light style chaser animation."""
    for j in range(256):
        for q in range(3):
            for i in range(0, neo.num_leds, 3):
                color = wheel((i + j) % 255)
                neo.set_led_color(i + q, color.red, color.green, color.blue, color.white)
            neo.update_strip(wait_ms / 1000.0)
            for i in range(0, neo.num_leds, 3):
                neo.set_led_color(i + q, 0, 0, 0, 0)
            neo.update_strip(0)  # Immediate update to clear

def extract_rgb(color: LEDColor) -> tuple:
    return (color.red, color.green, color.blue)

def move_color_closer(current_color: LEDColor, target_color: LEDColor, step: int = 1) -> LEDColor:
    """Move current color closer to target color by step."""
    def adjust_component(curr: int, targ: int, step: int) -> int:
        if curr < targ:
            return min(curr + step, targ)
        elif curr > targ:
            return max(curr - step, targ)
        return curr
    
    new_r = adjust_component(current_color.red, target_color.red, step)
    new_g = adjust_component(current_color.green, target_color.green, step)
    new_b = adjust_component(current_color.blue, target_color.blue, step)
    new_w = adjust_component(current_color.white, target_color.white, step)
    return LEDColor(new_r, new_g, new_b, new_w)

def fade(neo, start: LEDColor, end: LEDColor, wait_ms=100):
    """Fade from start color to end color."""
    current = start
    while current != end:
        current = move_color_closer(current, end)
        solidColor(neo, current, wait_ms / 1000.0)

def fade_in(neo, wait_ms=10):
    """Simulate fade-in by scaling brightness."""
    for i in range(256):
        scale = i / 255.0
        neo.fill_strip(int(255 * scale), int(255 * scale), int(255 * scale), int(255 * scale))
        neo.update_strip(wait_ms / 1000.0)

def fade_out(neo, wait_ms=10):
    """Simulate fade-out by scaling brightness."""
    for i in range(255, -1, -1):
        scale = i / 255.0
        neo.fill_strip(int(255 * scale), int(255 * scale), int(255 * scale), int(255 * scale))
        neo.update_strip(wait_ms / 1000.0)

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

    # Create Pi5Neo object
    try:
        neo = Pi5Neo(
            spi_device=SPI_DEVICE,
            num_leds=LED_COUNT,
            spi_speed_khz=SPI_SPEED_KHZ,
            pixel_type=PIXEL_TYPE,
            quiet_mode=QUIET_MODE
        )
    except Exception as e:
        print(f"Failed to initialize Pi5Neo: {e}")
        exit(1)

    # Map pattern names to functions and their default arguments
    pattern_map = {
        'fade-in': (fade_in, None),
        'fade-out': (fade_out, None),
        'solid': (solidColor, None),
        'colorwipe': (colorWipe, None),
        'theaterchase': (theaterChase, LEDColor(127, 127, 127)),
        'rainbow': (rainbow, None),
        'rainbowcycle': (rainbowCycle, None),
        'theaterchaserainbow': (theaterChaseRainbow, None),
        'fade': (fade, [LEDColor(255, 255, 0), LEDColor(0, 255, 255)])
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
                            raise ValueError("End RGB must be a tuple of 3 integers (0-255), e.g., (0,255,255)")
                        colors = [LEDColor(*start_rgb), LEDColor(*end_rgb)]
                    else:
                        # Expect one RGB tuple for other patterns
                        rgb = ast.literal_eval(pattern_parts[1])
                        if not (isinstance(rgb, tuple) and len(rgb) == 3 and all(isinstance(x, int) and 0 <= x <= 255 for x in rgb)):
                            raise ValueError("RGB must be a tuple of 3 integers (0-255), e.g., (255,255,0)")
                        colors = [LEDColor(*rgb)]
                except (ValueError, ValueError):
                    raise ValueError("Invalid RGB format. Use: (r,g,b), e.g., (255,255,0)")

            print(f"Running pattern: {pattern_name}")
            func, default_args = pattern_map[pattern_name]
            if pattern_name in ('fade-in', 'fade-out', 'rainbow', 'rainbowcycle', 'theaterchaserainbow'):
                func(neo)
            elif pattern_name == 'fade':
                start, end = colors if colors else default_args
                func(neo, start, end)
            else:
                # Apply brightness to color
                color = colors[0] if colors else default_args
                if color is None:
                    raise ValueError(f"Pattern {pattern_name} requires an RGB color, e.g., (255,255,0)")
                color = apply_brightness(color, args.brightness)
                func(neo, color)
        else:
            print('Press Ctrl-C to quit.')
            if not args.clear:
                print('Use "-c" argument to clear LEDs on exit')
            while True:
                cyan = apply_brightness(LEDColor(0,255,255), args.brightness)
                yellow = apply_brightness(LEDColor(255,255,0), args.brightness)
                red = apply_brightness(LEDColor(255,0,0), args.brightness)
                green = apply_brightness(LEDColor(0,0,0), args.brightness)
                blue = apply_brightness(LEDColor(0,0,255), args.brightness)
                white = apply_brightness(LEDColor(127,127,127), args.brightness)
                solidColor(neo, cyan)
                fade_out(neo)
                fade_in(neo)
                print('Color wipe animations.')
                solidColor(neo, yellow)
                colorWipe(neo, red)
                colorWipe(neo, green)
                colorWipe(neo, blue)
                print('Theater chase animations.')
                theaterChase(neo, white)
                theaterChase(neo, apply_brightness(LEDColor(127,0,0), args.brightness))
                theaterChase(neo, apply_brightness(LEDColor(0,0,127), args.brightness))
                print('Rainbow animations.')
                rainbow(neo)
                rainbowCycle(neo)
                theaterChaseRainbow(neo)

    except KeyboardInterrupt:
        if args.clear:
            neo.clear_strip()
            neo.update_strip()
    except Exception as e:
        print(f'Error: {e}')
        if args.clear:
            neo.clear_strip()
            neo.update_strip()

       
