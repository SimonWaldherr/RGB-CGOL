# RGB Colorful Game of Life

A colorful implementation of Conway's Game of Life using Python and Pygame.  
Each living cell carries an RGB color that evolves based on its neighbours,
producing dynamic, vibrant patterns.

Inspired by the [RGB-LED-Matrix](https://github.com/SimonWaldherr/RGB-LED-Matrix) project.  
Learn more about Conway's Game of Life on [Wikipedia](https://en.wikipedia.org/wiki/Conway%27s_Game_of_Life).  
and see implementations in many languages on the [GameOfLife repo](https://github.com/SimonWaldherr/GameOfLife).

## Requirements

- Python 3.x
- Pygame (`pip install pygame`)
- Pillow (`pip install pillow`)

## Usage

```bash
python rgb_cgol.py [options]
```

### Command-line options

| Option | Default | Description |
|--------|---------|-------------|
| `--width` | `128` | Number of columns in the field |
| `--height` | `128` | Number of rows in the field |
| `-d`, `--duration` | `-1` | Max frames to simulate (`-1` = run indefinitely) |
| `-f`, `--fps` | `20` | Target frames per second |
| `-o`, `--openfile` | *(none)* | Path to a `.txt` or `.png` file for the initial state |
| `-s`, `--cellsize` | `5` | Pixel size of each cell |
| `--fullscreen` | *(off)* | Run in fullscreen mode |
| `--mode` | `vibrant` | Colour-blending mode: `vibrant` or `average` |
| `--seed` | *(none)* | Integer random seed for reproducible runs |

### Keyboard shortcuts (during simulation)

| Key | Action |
|-----|--------|
| `SPACE` | Pause / unpause |
| `N` | Step one frame forward (while paused) |
| `R` | Reset to a fresh random field |
| `+` / `=` | Increase FPS by 5 |
| `-` | Decrease FPS by 5 (minimum 1) |
| `ESC` | Quit |

### Examples

1. Run with default parameters:
   ```bash
   python rgb_cgol.py
   ```

2. Run a 256×256 grid with 10 px cells at 60 FPS:
   ```bash
   python rgb_cgol.py --width 256 --height 256 -s 10 -f 60
   ```

3. Load an initial pattern from a text file:
   ```bash
   python rgb_cgol.py -o structures/01.txt
   ```

4. Run for exactly 500 frames at 30 FPS, then quit:
   ```bash
   python rgb_cgol.py -d 500 -f 30
   ```

5. Run fullscreen in average colour mode with a fixed seed:
   ```bash
   python rgb_cgol.py --fullscreen --mode average --seed 42
   ```

## Colour modes

- **vibrant** *(default)* – The dominant colour channel of living neighbours is
  boosted, keeping cells bright and contrasted.
- **average** – The new cell colour is the plain average of its living
  neighbours, producing softer gradients.

## Notes

- If no file is specified with `-o`, a random initial field is generated.
- The window title bar shows the current frame number, actual FPS, colour mode,
  and target FPS while the simulation is running.
- When paused, the title bar displays `PAUSED` instead of the live FPS.
- In fullscreen mode the field dimensions are recalculated automatically from
  the screen resolution and the chosen `--cellsize`.

## License

This project is licensed under the MIT License.
