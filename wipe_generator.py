# G-code generator for clearing an 850x350 mm sand table with horizontal lines
# Starting at (0,0), draws lines every N mm (default 10 mm)

# Table dimensions
TABLE_WIDTH = 850  # mm
TABLE_HEIGHT = 350  # mm
LINE_SPACING = 10  # mm, distance between horizontal lines
FEED_RATE = 1000    # mm/min, speed of movement (capped at 500 due to controller limit)

# Note: If feed rate is still limited, check your controller's max feed rate setting

# Generate G-code
gcode = []
# Initial setup: set units to mm, absolute positioning
gcode.append("G21 ; Set units to millimeters")
gcode.append("G90 ; Use absolute positioning")

# Start at (0,0)
gcode.append("G00 X0 Y0 ; Move to starting position")

# Generate horizontal lines
y = 0
while y <= TABLE_HEIGHT:
    # Move to start of line
    gcode.append(f"G01 X0 Y{y} F{FEED_RATE} ; Draw line to left")
    gcode.append(f"G01 X{TABLE_WIDTH} Y{y} F{FEED_RATE} ; Draw line to right")
    y += LINE_SPACING
    if y <= TABLE_HEIGHT:
        gcode.append(f"G01 x{TABLE_WIDTH} Y{y} F{FEED_RATE} ; Shift down")
        gcode.append(f"G01 X0 Y{y} F{FEED_RATE} ; Draw line to left")
        y += LINE_SPACING

# Lift tool and return to home
gcode.append("G00 X0 Y0 ; Return to home")

# Save G-code to file
with open("sand_table_clear.gcode", "w") as f:
    for line in gcode:
        f.write(line + "\n")

print("G-code generated and saved to 'sand_table_clear.gcode'")