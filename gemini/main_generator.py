# main_generator.py

import random
from sand_table_utils import SandTableGenerator, TABLE_WIDTH, TABLE_HEIGHT
from sand_table_patterns import (
    generate_spiro,
    generate_random_lines,
    generate_concentric_rectangles,
    generate_random_walk,
    generate_sine_wave
)

def generate_random_pattern(gcode_output="random_pattern.gcode", png_output="random_pattern.png"):
    generator = SandTableGenerator(gcode_output, png_output)

    # Define a list of pattern functions and their randomizable parameters
    patterns = [
        # Spirograph
        lambda: generate_spiro(
            generator,
            center_x=random.uniform(TABLE_WIDTH * 0.2, TABLE_WIDTH * 0.8),
            center_y=random.uniform(TABLE_HEIGHT * 0.2, TABLE_HEIGHT * 0.8),
            R=random.uniform(50, 150),
            r=random.uniform(10, 80),
            d=random.uniform(0.1, 100),
            num_revolutions=random.randint(5, 20),
            steps_per_revolution=random.randint(180, 500)
        ),
        # Random Lines
        lambda: generate_random_lines(
            generator,
            num_lines=random.randint(5, 20),
            max_length=random.uniform(50, 200),
            start_x=random.uniform(0, TABLE_WIDTH * 0.7),
            start_y=random.uniform(0, TABLE_HEIGHT * 0.7),
            end_x=random.uniform(TABLE_WIDTH * 0.3, TABLE_WIDTH),
            end_y=random.uniform(TABLE_HEIGHT * 0.3, TABLE_HEIGHT)
        ),
        # Concentric Rectangles
        lambda: generate_concentric_rectangles(
            generator,
            center_x=random.uniform(TABLE_WIDTH * 0.3, TABLE_WIDTH * 0.7),
            center_y=random.uniform(TABLE_HEIGHT * 0.3, TABLE_HEIGHT * 0.7),
            start_width=random.uniform(100, min(TABLE_WIDTH, TABLE_HEIGHT) * 0.8),
            start_height=random.uniform(100, min(TABLE_WIDTH, TABLE_HEIGHT) * 0.8),
            num_rects=random.randint(3, 10),
            spacing=random.uniform(5, 20)
        ),
        # Random Walk
        lambda: generate_random_walk(
            generator,
            start_x=random.uniform(0, TABLE_WIDTH),
            start_y=random.uniform(0, TABLE_HEIGHT),
            num_steps=random.randint(50, 300),
            step_length_min=random.uniform(2, 10),
            step_length_max=random.uniform(10, 30)
        ),
        # Sine Wave
        lambda: generate_sine_wave(
            generator,
            start_x=random.uniform(0, TABLE_WIDTH * 0.2),
            start_y=random.uniform(0, TABLE_HEIGHT),
            end_x=random.uniform(TABLE_WIDTH * 0.8, TABLE_WIDTH),
            end_y=random.uniform(0, TABLE_HEIGHT),
            amplitude=random.uniform(10, TABLE_HEIGHT / 4),
            frequency=random.uniform(1, 5),
            orientation=random.choice(['horizontal', 'vertical'])
        )
    ]

    # Choose a random number of patterns to combine
    num_elements = random.randint(1, 4) # You can adjust this

    # Clear the table before drawing new patterns (optional, but good for fresh starts)
    # You might want a "clear table" G-code sequence, like a full sweep.
    # For now, we'll just start drawing.

    # Execute a random selection of patterns
    selected_patterns = random.sample(patterns, num_elements)
    for pattern_func in selected_patterns:
        pattern_func() # Call the lambda function to generate the pattern

    generator.close()
    generator.save_png(png_output)

if __name__ == "__main__":
    random.seed() # Initialize random seed for truly random patterns each run
    print(f"Generating random pattern for sand table ({TABLE_WIDTH}x{TABLE_HEIGHT}mm)...")
    generate_random_pattern("rectangular_sand_pattern.gcode", "rectangular_sand_pattern.png")
    print("Pattern generation complete!")