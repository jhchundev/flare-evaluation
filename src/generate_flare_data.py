import numpy as np
import csv
import math

def create_flare_pattern(grid, center_x, center_y, light_radius=3, flare_radius=50, flare_intensity=0.3):
    """Create a light source with surrounding flare pattern."""
    height, width = grid.shape
    
    # Create bright light source (max 10-bit value)
    for dy in range(-light_radius, light_radius + 1):
        for dx in range(-light_radius, light_radius + 1):
            y, x = center_y + dy, center_x + dx
            if 0 <= y < height and 0 <= x < width:
                dist = math.sqrt(dx**2 + dy**2)
                if dist <= light_radius:
                    grid[y, x] = 1023  # Maximum 10-bit value
    
    # Create flare pattern around light
    for dy in range(-flare_radius, flare_radius + 1):
        for dx in range(-flare_radius, flare_radius + 1):
            y, x = center_y + dy, center_x + dx
            if 0 <= y < height and 0 <= x < width:
                dist = math.sqrt(dx**2 + dy**2)
                if light_radius < dist <= flare_radius:
                    # Exponential decay for flare
                    decay = math.exp(-dist / 15)
                    flare_value = flare_intensity * decay * 200
                    if flare_value > 10:  # Only add significant flare
                        current = grid[y, x]
                        if current < 1000:  # Don't overwrite light sources
                            grid[y, x] = min(250, current + flare_value)
    
    # Add cross-pattern flare (common in real optics)
    cross_length = flare_radius * 2
    cross_intensity = flare_intensity * 0.5
    
    # Horizontal streak
    for dx in range(-cross_length, cross_length + 1):
        x = center_x + dx
        if 0 <= x < width:
            dist = abs(dx)
            if dist > light_radius:
                decay = math.exp(-dist / 25)
                flare_value = cross_intensity * decay * 150
                if flare_value > 10:
                    current = grid[center_y, x]
                    if current < 1000:
                        grid[center_y, x] = min(250, current + flare_value)
    
    # Vertical streak
    for dy in range(-cross_length, cross_length + 1):
        y = center_y + dy
        if 0 <= y < height:
            dist = abs(dy)
            if dist > light_radius:
                decay = math.exp(-dist / 25)
                flare_value = cross_intensity * decay * 150
                if flare_value > 10:
                    current = grid[y, center_x]
                    if current < 1000:
                        grid[y, center_x] = min(250, current + flare_value)

def generate_flare_experiment_data(filename='flare_experiment_10bit.csv', size=512):
    """Generate 10-bit sensor data with light sources and flare patterns."""
    
    # Initialize grid with sensor noise around offset value
    offset = 64
    noise_std = 2
    grid = np.random.normal(offset, noise_std, (size, size))
    grid = np.clip(grid, 0, 1023)  # Ensure 10-bit range
    
    # Add multiple light sources with flare patterns
    light_positions = [
        (100, 100),   # Top-left
        (400, 100),   # Top-right
        (250, 250),   # Center
        (150, 400),   # Bottom-left
        (350, 350),   # Bottom-right offset
    ]
    
    for x, y in light_positions:
        create_flare_pattern(grid, x, y, 
                           light_radius=3, 
                           flare_radius=40 + np.random.randint(-10, 10),
                           flare_intensity=0.3 + np.random.uniform(-0.1, 0.1))
    
    # Add some smaller secondary light sources
    secondary_lights = [
        (200, 150),
        (300, 200),
        (180, 320),
    ]
    
    for x, y in secondary_lights:
        create_flare_pattern(grid, x, y,
                           light_radius=2,
                           flare_radius=25,
                           flare_intensity=0.2)
    
    # Add some random hot pixels (common in sensors)
    num_hot_pixels = 20
    for _ in range(num_hot_pixels):
        x = np.random.randint(0, size)
        y = np.random.randint(0, size)
        if grid[y, x] < 900:  # Don't overwrite light sources
            grid[y, x] = np.random.uniform(200, 400)
    
    # Ensure values are within 10-bit range
    grid = np.clip(grid, 0, 1023)
    
    # Save to CSV
    with open(filename, 'w', newline='') as f:
        writer = csv.writer(f)
        for row in grid:
            writer.writerow([f"{val:.2f}" for val in row])
    
    print(f"Generated {filename} with {len(light_positions)} primary and {len(secondary_lights)} secondary light sources")
    print(f"Data range: {grid.min():.2f} to {grid.max():.2f}")
    print(f"Mean value: {grid.mean():.2f}")
    
    # Calculate approximate flare statistics
    flare_pixels = np.sum((grid > (offset + 10)) & (grid < 250))
    light_pixels = np.sum(grid >= 1000)
    print(f"Approximate flare pixels: {flare_pixels}")
    print(f"Light source pixels: {light_pixels}")
    
    return grid

if __name__ == "__main__":
    data = generate_flare_experiment_data()