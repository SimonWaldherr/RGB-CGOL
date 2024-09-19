import pygame
import random
import sys
import os
import argparse
from PIL import Image

# Default parameters
DEFAULT_ROWS = 128
DEFAULT_COLS = 128
DEFAULT_BRIGHTNESS = 99
DEFAULT_FPS = 20
DEFAULT_DURATION = -1
DEFAULT_CELL_SIZE = 5
DEFAULT_COLOR_MODE = "rgb"  # Default to color mode

# Cell and Field classes
class Cell:
    def __init__(self, vitality=0, color=(0, 0, 0)):
        self.vitality = vitality  # Vitality of the cell
        self.color = color  # Color of the cell (can be RGB or grayscale)

class Field:
    def __init__(self, width, height):
        self.width = width  # Width of the field
        self.height = height  # Height of the field
        # Initialize a 2D list of cells
        self.cells = [[Cell() for _ in range(width)] for _ in range(height)]

    def set_vitality(self, x, y, vitality, color):
        # Ensure coordinates wrap around the field
        x = (x + self.width) % self.width
        y = (y + self.height) % self.height
        # Set cell vitality and color
        if vitality < 1:
            self.cells[y][x] = Cell(vitality=0, color=(0, 0, 0))
        else:
            self.cells[y][x] = Cell(vitality=vitality, color=color)

    def get_vitality(self, x, y):
        # Wrap around coordinates and return the cell at (x, y)
        x = (x + self.width) % self.width
        y = (y + self.height) % self.height
        return self.cells[y][x]

    def next_vitality(self, x, y):
        # Calculate the next vitality and color for the cell at (x, y)
        r, g, b = 0, 0, 0
        alive = 0
        # Check all neighboring cells
        for i in range(-1, 2):
            for j in range(-1, 2):
                if i == 0 and j == 0:
                    continue
                cell = self.get_vitality(x + i, y + j)
                if cell.vitality > 0:
                    alive += 1
                    r += cell.color[0]
                    g += cell.color[1]
                    b += cell.color[2]

        # Average color of neighboring cells
        if alive > 1:
            r, g, b = r // alive, g // alive, b // alive

        # Adjust color brightness
        if r + g + b < 400:
            if r >= g and r >= b:
                r = min(r + 100, 255)
            elif g >= b and g >= r:
                g = min(g + 100, 255)
            else:
                b = min(b + 100, 255)

        cell = self.get_vitality(x, y)
        # Apply rules of the game to determine the next state
        if alive == 3 or (alive == 2 and cell.vitality > 0):
            return Cell(vitality=min(cell.vitality + 1, 8), color=(r, g, b))
        
        return Cell(vitality=0, color=(0, 0, 0))

    def next_round(self):
        # Generate the next round of the game field
        new_field = Field(self.width, self.height)
        for y in range(self.height):
            for x in range(self.width):
                cell = self.next_vitality(x, y)
                new_field.set_vitality(x, y, cell.vitality, cell.color)
        return new_field

def generate_first_round(width, height, color_mode):
    # Initialize the field with random cells
    field = Field(width, height)
    for _ in range((width * height) // 4):
        if color_mode == "bw":
            # Generate grayscale color for black and white mode
            color = (255, 255, 255)
        else:
            # Generate random RGB color
            color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        
        field.set_vitality(
            random.randint(0, width - 1),
            random.randint(0, height - 1),
            1,
            color
        )
    return field

def load_first_round(width, height, filename):
    if not os.path.exists(filename):
        print(f"{filename} doesn't exist. Generating a random field.")
        return generate_first_round(width, height)

    field = Field(width, height)

    if filename.endswith(".png"):
        try:
            img = Image.open(filename).convert('RGB')
            img_width, img_height = img.size
            
            # Center the image if it's smaller than the field
            offset_x = (width - img_width) // 2 if img_width < width else 0
            offset_y = (height - img_height) // 2 if img_height < height else 0

            for y in range(min(img_height, height)):
                for x in range(min(img_width, width)):
                    r, g, b = img.getpixel((x, y))
                    if r > 128 or g > 128 or b > 128:
                        field.set_vitality(x + offset_x, y + offset_y, 9, (r, g, b))
                    elif r > 16 or g > 16 or b > 16:
                        field.set_vitality(x + offset_x, y + offset_y, 1, (r, g, b))
        except Exception as e:
            print(f"Error loading PNG file: {e}")
            return generate_first_round(width, height)

    elif filename.endswith(".txt"):
        try:
            with open(filename, 'r') as file:
                lines = file.readlines()

                # Determine the center position to start drawing the input
                max_width = max(len(line.rstrip()) for line in lines)
                max_height = len(lines)
                offset_x = (width - max_width) // 2 if max_width < width else 0
                offset_y = (height - max_height) // 2 if max_height < height else 0

                for y, line in enumerate(lines):
                    for x, char in enumerate(line.rstrip()):
                        if x < width and y < height:  # Ensure it fits within the field boundaries
                            if char == '1':
                                color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
                                field.set_vitality(x + offset_x, y + offset_y, 1, color)
                            elif char != ' ':
                                # Treat other characters as living cells
                                color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
                                field.set_vitality(x + offset_x, y + offset_y, 1, color)
        except Exception as e:
            print(f"Error loading text file: {e}")
            return generate_first_round(width, height)

    return field

def main():
    parser = argparse.ArgumentParser(description='Game of Life with adjustable parameters.')
    # Add color mode argument
    parser.add_argument('-cm', '--color_mode', type=str, default=DEFAULT_COLOR_MODE, help='Color mode of the game (rgb or bw)')
    parser.add_argument('-fw', '--width', type=int, default=DEFAULT_ROWS, help='Width of the field')
    parser.add_argument('-fh', '--height', type=int, default=DEFAULT_COLS, help='Height of the field')
    parser.add_argument('-d', '--duration', type=int, default=DEFAULT_DURATION, help='Game of Life duration')
    parser.add_argument('-f', '--fps', type=int, default=DEFAULT_FPS, help='Frames per second')
    parser.add_argument('-o', '--openfile', type=str, default="", help='File to open for the initial state')
    parser.add_argument('-s', '--cellsize', type=int, default=DEFAULT_CELL_SIZE, help='Size of each cell')
    parser.add_argument('--fullscreen', action='store_true', help='Run the game in fullscreen mode')
    args = parser.parse_args()

    pygame.init()

    if args.fullscreen:
        args.cellsize = args.cellsize + 2
        screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        # Adjust cell size and field dimensions based on screen size
        infoObject = pygame.display.Info()
        screen_width = infoObject.current_w
        screen_height = infoObject.current_h
        args.width = screen_width // args.cellsize
        args.height = screen_height // args.cellsize
    else:
        screen = pygame.display.set_mode((args.width * args.cellsize, args.height * args.cellsize))

    clock = pygame.time.Clock()

    # Generate or load the first round of cells
    field = load_first_round(args.width, args.height, args.openfile) if args.openfile else generate_first_round(args.width, args.height, args.color_mode)

    running = True
    iteration = 0

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            # Allow exiting fullscreen with ESC key
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

        # Render the field
        for y in range(field.height):
            for x in range(field.width):
                cell = field.get_vitality(x, y)
                rect = pygame.Rect(x * args.cellsize, y * args.cellsize, args.cellsize, args.cellsize)
                pygame.draw.rect(screen, cell.color, rect)
        
        pygame.display.flip()
        
        # Advance to the next round
        field = field.next_round()
        iteration += 1

        # Handle frame rate and duration
        clock.tick(args.fps)
        if args.duration != -1 and iteration >= args.duration:
            break

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
