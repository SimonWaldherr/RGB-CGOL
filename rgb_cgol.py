import pygame
import random
import sys
import os
import argparse
from PIL import Image

# Default parameters
DEFAULT_ROWS = 128
DEFAULT_COLS = 128
DEFAULT_FPS = 20
DEFAULT_DURATION = -1
DEFAULT_CELL_SIZE = 5
MODE_VIBRANT = 'vibrant'
MODE_AVERAGE = 'average'

# Cell and Field classes
class Cell:
    def __init__(self, vitality=0, color=(0, 0, 0)):
        self.vitality = vitality  # Vitality of the cell
        self.color = color  # Color of the cell (RGB tuple)

class Field:
    def __init__(self, width, height, mode=MODE_VIBRANT):
        self.width = width  # Width of the field
        self.height = height  # Height of the field
        self.mode = mode  # Game mode ('vibrant' or 'average')
        # Initialize a 2D array of cells
        self.cells = [[Cell() for _ in range(width)] for _ in range(height)]

    def set_vitality(self, x, y, vitality, color):
        # Keep coordinates within the field (wrap-around)
        x = (x + self.width) % self.width
        y = (y + self.height) % self.height
        # Set the vitality and color of the cell
        if vitality < 1:
            self.cells[y][x] = Cell(vitality=0, color=(0, 0, 0))
        else:
            self.cells[y][x] = Cell(vitality=vitality, color=color)

    def get_vitality(self, x, y):
        # Keep coordinates within the field (wrap-around)
        x = (x + self.width) % self.width
        y = (y + self.height) % self.height
        return self.cells[y][x]

    def next_vitality(self, x, y):
        cell = self.get_vitality(x, y)
        r_sum, g_sum, b_sum = 0, 0, 0
        alive = 0
        # Check all neighboring cells
        for i in range(-1, 2):
            for j in range(-1, 2):
                if i == 0 and j == 0:
                    continue
                neighbor_cell = self.get_vitality(x + i, y + j)
                if neighbor_cell.vitality > 0:
                    alive += 1
                    r_sum += neighbor_cell.color[0]
                    g_sum += neighbor_cell.color[1]
                    b_sum += neighbor_cell.color[2]
        # Compute average color
        if alive > 0:
            r_avg = r_sum // alive
            g_avg = g_sum // alive
            b_avg = b_sum // alive
        else:
            r_avg, g_avg, b_avg = 0, 0, 0

        if self.mode == MODE_VIBRANT:
            # Vibrant mode adjustments
            if alive > 1:
                r, g, b = r_avg, g_avg, b_avg
            else:
                r, g, b = r_sum, g_sum, b_sum

            # Adjust brightness
            if r + g + b < 400:
                if r >= g and r >= b:
                    r += 100
                    g -= 50
                    b -= 50
                elif g >= r and g >= b:
                    r -= 50
                    g += 100
                    b -= 50
                elif b >= r and b >= g:
                    r -= 50
                    g -= 50
                    b += 100
        elif self.mode == MODE_AVERAGE:
            # Average mode adjustments
            r, g, b = r_avg, g_avg, b_avg
            # Adjust brightness
            if r + g + b < 400:
                if r >= g and r >= b:
                    r = min(r + 100, 255)
                elif g >= r and g >= b:
                    g = min(g + 100, 255)
                else:
                    b = min(b + 100, 255)
        else:
            # Default behavior
            r, g, b = r_avg, g_avg, b_avg

        # Clamp color values
        r = min(max(0, r), 255)
        g = min(max(0, g), 255)
        b = min(max(0, b), 255)

        # Apply Game of Life rules
        if alive == 3 or (alive == 2 and cell.vitality > 0):
            vitality = min(cell.vitality + 1, 8)
            return Cell(vitality=vitality, color=(r, g, b))
        else:
            return Cell(vitality=0, color=(0, 0, 0))

    def next_round(self):
        # Generate the next field based on the current state
        new_field = Field(self.width, self.height, self.mode)
        for y in range(self.height):
            for x in range(self.width):
                cell = self.next_vitality(x, y)
                new_field.set_vitality(x, y, cell.vitality, cell.color)
        return new_field

    def print_field(self, screen, cell_size):
        # Draw the current field on the screen
        for y in range(self.height):
            for x in range(self.width):
                cell = self.get_vitality(x, y)
                rect = pygame.Rect(x * cell_size, y * cell_size, cell_size, cell_size)
                if cell.vitality > 0:
                    pygame.draw.rect(screen, cell.color, rect)
                else:
                    pygame.draw.rect(screen, (0, 0, 0), rect)
        pygame.display.flip()

def generate_first_round(width, height, mode=MODE_VIBRANT):
    # Initialize the field with random cells
    field = Field(width, height, mode=mode)
    for _ in range((width * height) // 4):
        color = (
            random.randint(0, 255),
            random.randint(0, 255),
            random.randint(0, 255)
        )
        field.set_vitality(
            random.randint(0, width - 1),
            random.randint(0, height - 1),
            1,
            color
        )
    return field

def load_first_round(width, height, filename, mode=MODE_VIBRANT):
    if not os.path.exists(filename):
        print(f"{filename} doesn't exist. Generating a random field.")
        return generate_first_round(width, height, mode)

    field = Field(width, height, mode=mode)

    if filename.endswith(".txt"):
        try:
            with open(filename, 'r') as file:
                lines = file.readlines()

                # Center the image if it's smaller than the field
                max_width = max(len(line.rstrip()) for line in lines)
                max_height = len(lines)
                offset_x = (width - max_width) // 2 if max_width < width else 0
                offset_y = (height - max_height) // 2 if max_height < height else 0

                for y, line in enumerate(lines):
                    for x, char in enumerate(line.rstrip()):
                        if x < width and y < height:
                            if char in '123456789':
                                vitality = int(char)
                                color = (
                                    random.randint(0, 255),
                                    random.randint(0, 255),
                                    random.randint(0, 255)
                                )
                                field.set_vitality(x + offset_x, y + offset_y, vitality, color)
                            elif char != ' ':
                                # Treat other characters as living cells with vitality 1
                                color = (
                                    random.randint(0, 255),
                                    random.randint(0, 255),
                                    random.randint(0, 255)
                                )
                                field.set_vitality(x + offset_x, y + offset_y, 1, color)
        except Exception as e:
            print(f"Error loading text file: {e}")
            return generate_first_round(width, height, mode)
    elif filename.endswith(".png"):
        try:
            img = Image.open(filename).convert('RGB')
            img = img.resize((width, height))
            for y in range(height):
                for x in range(width):
                    r, g, b = img.getpixel((x, y))
                    if r > 128 or g > 128 or b > 128:
                        field.set_vitality(x, y, 9, (r, g, b))
                    elif r > 16 or g > 16 or b > 16:
                        field.set_vitality(x, y, 1, (r, g, b))
        except Exception as e:
            print(f"Error loading PNG file: {e}")
            return generate_first_round(width, height, mode)
    else:
        print("Unknown file format. Generating a random field.")
        return generate_first_round(width, height, mode)

    return field

def main():
    parser = argparse.ArgumentParser(description='Game of Life with adjustable parameters.')
    parser.add_argument('--width', type=int, default=DEFAULT_ROWS, help='Width of the field')
    parser.add_argument('--height', type=int, default=DEFAULT_COLS, help='Height of the field')
    parser.add_argument('-d', '--duration', type=int, default=DEFAULT_DURATION, help='Duration of the game')
    parser.add_argument('-f', '--fps', type=int, default=DEFAULT_FPS, help='Frames per second')
    parser.add_argument('-o', '--openfile', type=str, default="", help='File to open for initial state')
    parser.add_argument('-s', '--cellsize', type=int, default=DEFAULT_CELL_SIZE, help='Size of each cell in pixels')
    parser.add_argument('--fullscreen', action='store_true', help='Run the game in fullscreen mode')
    parser.add_argument('--mode', type=str, choices=[MODE_VIBRANT, MODE_AVERAGE], default=MODE_VIBRANT, help='Game mode to play')
    args = parser.parse_args()

    pygame.init()

    if args.fullscreen:
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

    # Generate or load the first state of the field
    if args.openfile:
        field = load_first_round(args.width, args.height, args.openfile, mode=args.mode)
    else:
        field = generate_first_round(args.width, args.height, mode=args.mode)

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

        # Draw the field
        field.print_field(screen, args.cellsize)

        # Compute the next round
        field = field.next_round()
        iteration += 1

        # Manage frame rate and duration
        clock.tick(args.fps)
        if args.duration != -1 and iteration >= args.duration:
            break

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
