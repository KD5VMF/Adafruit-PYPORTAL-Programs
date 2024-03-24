import time
import board
import displayio
import random
from adafruit_display_shapes.rect import Rect

# Game parameters
CELL_SIZE = 20  # Adjusted for optimal display on PyPortal 20
GRID_WIDTH = 16  # Optimized grid width 16
GRID_HEIGHT = 12  # Optimized grid height 12
MAX_ITERATIONS = 50 # 300
UPDATE_INTERVAL = 0.1  # Reduced update interval for smoother animations 0.1

def create_grid():
    """Create a new grid with random initial states."""
    return [[random.choice([0, 1]) for _ in range(GRID_HEIGHT)] for _ in range(GRID_WIDTH)]

def create_grid_display(group):
    """Create and return a list of rectangle objects for display."""
    rects = []
    for x in range(GRID_WIDTH):
        row = []
        for y in range(GRID_HEIGHT):
            rect = Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE, fill=0x000000)
            group.append(rect)
            row.append(rect)
        rects.append(row)
    return rects

def update_grid_display(grid, rects):
    """Update the display based on the current grid state."""
    for x in range(GRID_WIDTH):
        for y in range(GRID_HEIGHT):
            rects[x][y].fill = 0x00FF00 if grid[x][y] else 0x000000

def count_neighbors(grid, x, y):
    """Count alive neighbors around a given cell."""
    return sum(grid[(x + dx) % GRID_WIDTH][(y + dy) % GRID_HEIGHT] for dx in [-1, 0, 1] for dy in [-1, 0, 1] if (dx, dy) != (0, 0))

def update_grid(grid):
    """Update the grid for the next generation."""
    new_grid = [[grid[x][y] for y in range(GRID_HEIGHT)] for x in range(GRID_WIDTH)]
    for x in range(GRID_WIDTH):
        for y in range(GRID_HEIGHT):
            neighbors = count_neighbors(grid, x, y)
            new_grid[x][y] = 1 if (grid[x][y] and neighbors in [2, 3]) or (not grid[x][y] and neighbors == 3) else 0
    return new_grid

def main():
    display = board.DISPLAY
    group = displayio.Group()
    display.show(group)

    grid = create_grid()
    rects = create_grid_display(group)

    iterations = 0
    while True:
        time.sleep(UPDATE_INTERVAL)
        grid = update_grid(grid)
        update_grid_display(grid, rects)
        iterations += 1
        if iterations >= MAX_ITERATIONS:
            grid = create_grid()
            iterations = 0

if __name__ == "__main__":
    main()
