"""
RGB Colorful Game of Life
=========================
A colorful implementation of Conway's Game of Life using Python and Pygame.
Each living cell carries an RGB color that evolves based on its neighbours,
producing dynamic, vibrant patterns.

Keyboard controls (at runtime):
  SPACE   – pause / unpause
  N       – advance one frame while paused
  R       – reset to a new random field (keeps current settings)
  +       – increase FPS by 5
  -       – decrease FPS by 5 (minimum 1)
  ESC     – quit
"""

import pygame
import random
import sys
import os
import argparse
from PIL import Image

# ---------------------------------------------------------------------------
# Default simulation parameters
# ---------------------------------------------------------------------------
DEFAULT_WIDTH = 128       # Default number of columns
DEFAULT_HEIGHT = 128      # Default number of rows
DEFAULT_FPS = 20          # Default frames per second
DEFAULT_DURATION = -1     # -1 means run indefinitely
DEFAULT_CELL_SIZE = 5     # Default pixel size of each cell

# Colour-blending mode identifiers
MODE_VIBRANT = 'vibrant'  # Boost the dominant channel for vivid colours
MODE_AVERAGE = 'average'  # Use the plain average of neighbour colours


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

class Cell:
    """Represents a single cell in the Game of Life grid.

    Attributes:
        vitality (int): 0 = dead, 1–8 = alive (increases each surviving step).
        color (tuple): RGB colour tuple (0–255 per channel).
    """

    def __init__(self, vitality=0, color=(0, 0, 0)):
        self.vitality = vitality
        self.color = color


class Field:
    """The game board – a 2-D grid of :class:`Cell` objects.

    Attributes:
        width  (int): Number of columns.
        height (int): Number of rows.
        mode   (str): Colour-blending mode (``MODE_VIBRANT`` or ``MODE_AVERAGE``).
        cells  (list[list[Cell]]): 2-D array of cells indexed as [row][col].
    """

    def __init__(self, width, height, mode=MODE_VIBRANT):
        self.width = width
        self.height = height
        self.mode = mode
        # Initialise every cell as dead (vitality=0, black)
        self.cells = [[Cell() for _ in range(width)] for _ in range(height)]

    def set_vitality(self, x, y, vitality, color):
        """Set the state of the cell at (x, y) with wrap-around coordinates.

        A vitality below 1 kills the cell (sets it to dead/black).
        """
        x = (x + self.width) % self.width
        y = (y + self.height) % self.height
        if vitality < 1:
            self.cells[y][x] = Cell(vitality=0, color=(0, 0, 0))
        else:
            self.cells[y][x] = Cell(vitality=vitality, color=color)

    def get_vitality(self, x, y):
        """Return the :class:`Cell` at (x, y) using wrap-around coordinates."""
        x = (x + self.width) % self.width
        y = (y + self.height) % self.height
        return self.cells[y][x]

    def _blend_color(self, r_sum, g_sum, b_sum, alive):
        """Compute the blended colour for a new or surviving cell.

        Depending on :attr:`mode`, either average the neighbour colours
        (``MODE_AVERAGE``) or use a vibrant channel-boost approach
        (``MODE_VIBRANT``).  The dominant channel is boosted when the
        combined brightness is low so that cells never fade to near-black.

        Returns:
            tuple: Clamped (r, g, b) values in the range 0–255.
        """
        if alive > 0:
            r_avg = r_sum // alive
            g_avg = g_sum // alive
            b_avg = b_sum // alive
        else:
            r_avg = g_avg = b_avg = 0

        if self.mode == MODE_VIBRANT:
            # Use the raw sum when there is only one alive neighbour so
            # that single-neighbour births inherit a bright colour.
            r, g, b = (r_avg, g_avg, b_avg) if alive > 1 else (r_sum, g_sum, b_sum)
            # Boost the dominant channel when the cell would be too dark
            if r + g + b < 400:
                if r >= g and r >= b:
                    r, g, b = min(r + 100, 255), max(g - 50, 0), max(b - 50, 0)
                elif g >= r and g >= b:
                    r, g, b = max(r - 50, 0), min(g + 100, 255), max(b - 50, 0)
                else:
                    r, g, b = max(r - 50, 0), max(g - 50, 0), min(b + 100, 255)
        elif self.mode == MODE_AVERAGE:
            r, g, b = r_avg, g_avg, b_avg
            # Boost only the dominant channel when too dark
            if r + g + b < 400:
                if r >= g and r >= b:
                    r = min(r + 100, 255)
                elif g >= r and g >= b:
                    g = min(g + 100, 255)
                else:
                    b = min(b + 100, 255)
        else:
            # Fallback: plain average
            r, g, b = r_avg, g_avg, b_avg

        # Clamp all channels to the valid 0–255 range
        r = min(max(0, r), 255)
        g = min(max(0, g), 255)
        b = min(max(0, b), 255)
        return r, g, b

    def next_vitality(self, x, y):
        """Compute the next-generation :class:`Cell` for position (x, y).

        Applies standard Conway's Game of Life survival rules:
          * A live cell with 2 or 3 live neighbours survives.
          * A dead cell with exactly 3 live neighbours is born.
          * All other cells die or remain dead.

        In addition, a surviving cell's vitality increases by 1 each step
        (capped at 8), and the colour is blended from living neighbours.
        """
        cell = self.get_vitality(x, y)
        r_sum = g_sum = b_sum = 0
        alive = 0

        # Inspect all 8 Moore neighbours
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                if dx == 0 and dy == 0:
                    continue  # Skip the cell itself
                neighbour = self.get_vitality(x + dx, y + dy)
                if neighbour.vitality > 0:
                    alive += 1
                    r_sum += neighbour.color[0]
                    g_sum += neighbour.color[1]
                    b_sum += neighbour.color[2]

        r, g, b = self._blend_color(r_sum, g_sum, b_sum, alive)

        # Conway's rules: born with 3 neighbours, survives with 2 or 3
        if alive == 3 or (alive == 2 and cell.vitality > 0):
            new_vitality = min(cell.vitality + 1, 8)
            return Cell(vitality=new_vitality, color=(r, g, b))
        else:
            return Cell(vitality=0, color=(0, 0, 0))

    def next_round(self):
        """Compute and return the entire next-generation :class:`Field`."""
        new_field = Field(self.width, self.height, self.mode)
        for y in range(self.height):
            for x in range(self.width):
                cell = self.next_vitality(x, y)
                new_field.set_vitality(x, y, cell.vitality, cell.color)
        return new_field

    def draw_field(self, screen, cell_size):
        """Render the current field onto *screen* using the given *cell_size*.

        Dead cells are drawn as black rectangles; living cells use their
        stored RGB colour.  The display is flipped once after all cells
        have been drawn.
        """
        for y in range(self.height):
            for x in range(self.width):
                cell = self.get_vitality(x, y)
                rect = pygame.Rect(x * cell_size, y * cell_size, cell_size, cell_size)
                color = cell.color if cell.vitality > 0 else (0, 0, 0)
                pygame.draw.rect(screen, color, rect)
        pygame.display.flip()


# ---------------------------------------------------------------------------
# Field initialisation helpers
# ---------------------------------------------------------------------------

def generate_first_round(width, height, mode=MODE_VIBRANT):
    """Create a :class:`Field` populated with a random assortment of cells.

    Roughly one quarter of all cells are seeded as alive with a random
    RGB colour.
    """
    field = Field(width, height, mode=mode)
    for _ in range((width * height) // 4):
        color = (
            random.randint(0, 255),
            random.randint(0, 255),
            random.randint(0, 255),
        )
        field.set_vitality(
            random.randint(0, width - 1),
            random.randint(0, height - 1),
            1,
            color,
        )
    return field


def load_first_round(width, height, filename, mode=MODE_VIBRANT):
    """Load an initial :class:`Field` from *filename*.

    Supported formats:
      * ``.txt`` – plain-text pattern files (non-space characters = alive cell;
        digit characters 1–9 set the initial vitality directly).
      * ``.png`` – image files (bright pixels become alive cells).

    The pattern is centred on the field when it is smaller than the field.
    Falls back to :func:`generate_first_round` on any error.
    """
    if not os.path.exists(filename):
        print(f"{filename} doesn't exist. Generating a random field.")
        return generate_first_round(width, height, mode)

    field = Field(width, height, mode=mode)

    if filename.endswith(".txt"):
        try:
            with open(filename, 'r') as file:
                lines = file.readlines()

            # Centre the pattern within the field when it is smaller
            max_width = max((len(line.rstrip()) for line in lines), default=0)
            max_height = len(lines)
            offset_x = (width - max_width) // 2 if max_width < width else 0
            offset_y = (height - max_height) // 2 if max_height < height else 0

            for y, line in enumerate(lines):
                for x, char in enumerate(line.rstrip()):
                    if x >= width or y >= height:
                        continue
                    if char in '123456789':
                        vitality = int(char)
                    elif char == ' ':
                        continue  # Space = dead cell
                    else:
                        vitality = 1  # Any other non-space character = alive

                    color = (
                        random.randint(0, 255),
                        random.randint(0, 255),
                        random.randint(0, 255),
                    )
                    field.set_vitality(x + offset_x, y + offset_y, vitality, color)
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


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def main():
    """Parse command-line arguments, initialise Pygame, and run the simulation.

    Keyboard shortcuts during the simulation:
      SPACE  – pause / unpause
      N      – step one frame forward (only while paused)
      R      – reset to a fresh random field
      +      – increase FPS by 5
      -      – decrease FPS by 5 (minimum 1)
      ESC    – quit
    """
    parser = argparse.ArgumentParser(
        description='Colorful Conway\'s Game of Life powered by Pygame.',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument('--width',       type=int,   default=DEFAULT_WIDTH,     help='Number of columns in the field')
    parser.add_argument('--height',      type=int,   default=DEFAULT_HEIGHT,    help='Number of rows in the field')
    parser.add_argument('-d', '--duration', type=int, default=DEFAULT_DURATION, help='Max frames to simulate (-1 = infinite)')
    parser.add_argument('-f', '--fps',   type=int,   default=DEFAULT_FPS,       help='Target frames per second')
    parser.add_argument('-o', '--openfile', type=str, default='',              help='Path to a .txt or .png file for the initial state')
    parser.add_argument('-s', '--cellsize', type=int, default=DEFAULT_CELL_SIZE, help='Pixel size of each cell')
    parser.add_argument('--fullscreen',  action='store_true',                   help='Run in fullscreen mode')
    parser.add_argument('--mode',        type=str,   choices=[MODE_VIBRANT, MODE_AVERAGE],
                        default=MODE_VIBRANT,                                   help='Colour-blending mode')
    parser.add_argument('--seed',        type=int,   default=None,              help='Random seed for reproducible runs')
    args = parser.parse_args()

    # Seed the random number generator when requested
    if args.seed is not None:
        random.seed(args.seed)

    pygame.init()

    if args.fullscreen:
        screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        # Recalculate field dimensions to fill the screen exactly
        info = pygame.display.Info()
        args.width  = info.current_w // args.cellsize
        args.height = info.current_h // args.cellsize
    else:
        screen = pygame.display.set_mode((args.width * args.cellsize, args.height * args.cellsize))

    pygame.display.set_caption('RGB Colorful Game of Life')
    clock = pygame.time.Clock()

    # ------------------------------------------------------------------
    # Helper: (re-)build the initial field
    # ------------------------------------------------------------------
    def build_field():
        if args.openfile:
            return load_first_round(args.width, args.height, args.openfile, mode=args.mode)
        return generate_first_round(args.width, args.height, mode=args.mode)

    field = build_field()
    fps = args.fps     # Current FPS (can be adjusted at runtime)
    paused = False
    iteration = 0

    # ------------------------------------------------------------------
    # Main simulation loop
    # ------------------------------------------------------------------
    running = True
    while running:
        # ---- Event handling ------------------------------------------
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

                elif event.key == pygame.K_SPACE:
                    # Toggle pause
                    paused = not paused

                elif event.key == pygame.K_n and paused:
                    # Advance a single frame while paused
                    field.draw_field(screen, args.cellsize)
                    field = field.next_round()
                    iteration += 1

                elif event.key == pygame.K_r:
                    # Reset to a fresh random field
                    if args.seed is not None:
                        random.seed(args.seed)
                    field = build_field()
                    iteration = 0
                    paused = False

                elif event.key in (pygame.K_PLUS, pygame.K_EQUALS, pygame.K_KP_PLUS):
                    # Increase FPS
                    fps = min(fps + 5, 120)

                elif event.key in (pygame.K_MINUS, pygame.K_KP_MINUS):
                    # Decrease FPS (never below 1)
                    fps = max(fps - 5, 1)

        # ---- Update window title with live stats ---------------------
        status = 'PAUSED' if paused else f'{clock.get_fps():.0f} FPS'
        pygame.display.set_caption(
            f'RGB Colorful GoL  |  frame {iteration}  |  {status}  |  '
            f'mode: {args.mode}  |  target: {fps} FPS'
        )

        # ---- Render and advance (skip when paused) -------------------
        if not paused:
            field.draw_field(screen, args.cellsize)
            field = field.next_round()
            iteration += 1

        # ---- Frame-rate cap and duration check -----------------------
        clock.tick(fps)
        if args.duration != -1 and iteration >= args.duration:
            break

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
