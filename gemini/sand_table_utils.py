# sand_table_utils.py

import math
from PIL import Image, ImageDraw

# Sand table dimensions in mm
TABLE_WIDTH = 850
TABLE_HEIGHT = 350

# G-code settings
Z_DOWN = -0.5  # Z-coordinate for drawing (e.g., slightly below surface)
Z_UP = 0.5     # Z-coordinate for lifting (e.g., above surface)
FEED_RATE = 2000 # mm/min

class SandTableGenerator:
    def __init__(self, output_gcode_path="pattern.gcode", output_png_path="pattern.png"):
        self.gcode_file = open(output_gcode_path, "w")
        self.gcode_file.write("G90 ; Absolute positioning\n")
        self.gcode_file.write("G21 ; Millimeters\n")
        self.gcode_file.write("G28 ; Home all axes (optional, uncomment if you have homing)\n")
        self.gcode_file.write(f"G0 Z{Z_UP} F{FEED_RATE} ; Lift pen\n") # Start with pen up
        self.current_x = None
        self.current_y = None

        self.image = Image.new("RGB", (TABLE_WIDTH, TABLE_HEIGHT), (255, 255, 255)) # White background
        self.draw = ImageDraw.Draw(self.image)
        self.scale_factor_x = 1 # We'll draw directly in mm for the PNG
        self.scale_factor_y = 1 # We'll draw directly in mm for the PNG

    def _clamp_coordinates(self, x, y):
        x = max(0, min(x, TABLE_WIDTH))
        y = max(0, min(y, TABLE_HEIGHT))
        return x, y

    def move_to(self, x, y, pen_down=False):
        x, y = self._clamp_coordinates(x, y)

        if self.current_x is not None and self.current_y is not None and pen_down:
            # Draw line on PNG
            self.draw.line(
                (self.current_x * self.scale_factor_x, self.current_y * self.scale_factor_y,
                 x * self.scale_factor_x, y * self.scale_factor_y),
                fill=(0, 0, 0), # Black line
                width=1
            )

        if pen_down:
            self.gcode_file.write(f"G1 Z{Z_DOWN} F{FEED_RATE} ; Pen down\n")
            self.gcode_file.write(f"G1 X{x:.3f} Y{y:.3f} F{FEED_RATE} ; Move with pen down\n")
        else:
            self.gcode_file.write(f"G0 Z{Z_UP} F{FEED_RATE} ; Pen up\n")
            self.gcode_file.write(f"G0 X{x:.3f} Y{y:.3f} F{FEED_RATE} ; Move with pen up\n")

        self.current_x = x
        self.current_y = y

    def close(self):
        self.gcode_file.write(f"G0 Z{Z_UP} F{FEED_RATE} ; Lift pen\n")
        self.gcode_file.write("G0 X0 Y0 F2000 ; Return to origin (optional)\n")
        self.gcode_file.write("M2 ; End of program\n")
        self.gcode_file.close()
        print(f"G-code saved to {self.gcode_file.name}")

    def save_png(self, path="pattern.png"):
        self.image.save(path)
        print(f"PNG preview saved to {path}")

# Example usage within a pattern function
# generator = SandTableGenerator()
# generator.move_to(10, 10, pen_down=False)
# generator.move_to(50, 50, pen_down=True)
# generator.close()
# generator.save_png()
