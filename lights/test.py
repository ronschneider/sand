from rpi_ws281x import PixelStrip, Color
LED_COUNT = 30
LED_PIN = 18
strip = PixelStrip(LED_COUNT, LED_PIN)
strip.begin()
for i in range(strip.numPixels()):
    strip.setPixelColor(i, Color(255, 0, 0))
strip.show()

