# sand_table_patterns.py

import random
import math
from sand_table_utils import SandTableGenerator, TABLE_WIDTH, TABLE_HEIGHT, Z_UP, Z_DOWN, FEED_RATE

def generate_spiro(generator: SandTableGenerator,
                   center_x: float, center_y: float,
                   R: float, r: float, d: float,
                   num_revolutions: int = 10,
                   steps_per_revolution: int = 360):
    """
    Generates a spirograph pattern.
    R: Radius of the fixed circle
    r: Radius of the rolling circle
    d: Distance of the pen from the center of the rolling circle
    """
    path_points = []
    max_t = num_revolutions * 2 * math.pi
    step_size = (2 * math.pi) / steps_per_revolution

    first_point = True
    for t in range(int(max_t / step_size)):
        theta = t * step_size
        x = center_x + (R - r) * math.cos(theta) + d * math.cos(((R - r) / r) * theta)
        y = center_y + (R - r) * math.sin(theta) - d * math.sin(((R - r) / r) * theta) # Y-axis inverted for sand table often

        # Ensure points are within table boundaries
        x = max(0, min(x, TABLE_WIDTH))
        y = max(0, min(y, TABLE_HEIGHT))

        path_points.append((x, y))

        if first_point:
            generator.move_to(x, y, pen_down=False) # Move to start without drawing
            first_point = False
        else:
            generator.move_to(x, y, pen_down=True) # Draw the path

    generator.move_to(path_points[-1][0], path_points[-1][1], pen_down=False) # Lift pen at end

def generate_random_lines(generator: SandTableGenerator,
                          num_lines: int,
                          max_length: float,
                          start_x: float, start_y: float,
                          end_x: float, end_y: float):
    """
    Generates a series of random lines within a bounding box.
    """
    for _ in range(num_lines):
        x1 = random.uniform(start_x, end_x)
        y1 = random.uniform(start_y, end_y)

        # Ensure lines don't go too far out, or just clamp their ends
        angle = random.uniform(0, 2 * math.pi)
        length = random.uniform(max_length * 0.2, max_length)

        x2 = x1 + length * math.cos(angle)
        y2 = y1 + length * math.sin(angle)

        generator.move_to(x1, y1, pen_down=False)
        generator.move_to(x2, y2, pen_down=True)
    generator.move_to(x2, y2, pen_down=False) # Lift pen after last line

def generate_concentric_rectangles(generator: SandTableGenerator,
                                   center_x: float, center_y: float,
                                   start_width: float, start_height: float,
                                   num_rects: int,
                                   spacing: float):
    """
    Generates concentric rectangles.
    """
    for i in range(num_rects):
        width = start_width - i * spacing * 2
        height = start_height - i * spacing * 2

        if width <= 0 or height <= 0:
            break

        half_width = width / 2
        half_height = height / 2

        x_min = center_x - half_width
        y_min = center_y - half_height
        x_max = center_x + half_width
        y_max = center_y + half_height

        # Clamp points to table boundaries
        x_min = max(0, x_min)
        y_min = max(0, y_min)
        x_max = min(TABLE_WIDTH, x_max)
        y_max = min(TABLE_HEIGHT, y_max)

        # Move to first corner (top-left)
        generator.move_to(x_min, y_min, pen_down=False)
        # Draw rectangle
        generator.move_to(x_max, y_min, pen_down=True)
        generator.move_to(x_max, y_max, pen_down=True)
        generator.move_to(x_min, y_max, pen_down=True)
        generator.move_to(x_min, y_min, pen_down=True) # Close the rectangle
    generator.move_to(center_x, center_y, pen_down=False) # Lift pen at end

def generate_random_walk(generator: SandTableGenerator,
                         start_x: float, start_y: float,
                         num_steps: int,
                         step_length_min: float, step_length_max: float):
    """
    Generates a random walk pattern.
    """
    current_x = start_x
    current_y = start_y

    generator.move_to(current_x, current_y, pen_down=False)

    for _ in range(num_steps):
        angle = random.uniform(0, 2 * math.pi)
        step_len = random.uniform(step_length_min, step_length_max)

        next_x = current_x + step_len * math.cos(angle)
        next_y = current_y + step_len * math.sin(angle)

        # Clamp to boundaries
        next_x = max(0, min(next_x, TABLE_WIDTH))
        next_y = max(0, min(next_y, TABLE_HEIGHT))

        generator.move_to(next_x, next_y, pen_down=True)

        current_x = next_x
        current_y = next_y
    generator.move_to(current_x, current_y, pen_down=False) # Lift pen at end

def generate_sine_wave(generator: SandTableGenerator,
                       start_x: float, start_y: float,
                       end_x: float, end_y: float,
                       amplitude: float,
                       frequency: float,
                       num_points: int = 200,
                       orientation: str = 'horizontal'):
    """
    Generates a sine wave.
    orientation: 'horizontal' or 'vertical'
    """
    path_points = []
    if orientation == 'horizontal':
        for i in range(num_points):
            t = i / (num_points - 1)
            x = start_x + t * (end_x - start_x)
            y = start_y + amplitude * math.sin(frequency * t * 2 * math.pi)
            path_points.append((x, y))
    elif orientation == 'vertical':
        for i in range(num_points):
            t = i / (num_points - 1)
            y = start_y + t * (end_y - start_y)
            x = start_x + amplitude * math.sin(frequency * t * 2 * math.pi)
            path_points.append((x, y))
    else:
        raise ValueError("Orientation must be 'horizontal' or 'vertical'")

    # Move to first point without drawing
    if path_points:
        generator.move_to(path_points[0][0], path_points[0][1], pen_down=False)
        for x, y in path_points:
            # Clamp points to boundaries
            x = max(0, min(x, TABLE_WIDTH))
            y = max(0, min(y, TABLE_HEIGHT))
            generator.move_to(x, y, pen_down=True)
    generator.move_to(path_points[-1][0], path_points[-1][1], pen_down=False) # Lift pen at end