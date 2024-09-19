# Colorful Game of Life with Pygame

A simple implementation of Conway's Game of Life using Python and Pygame, featuring adjustable parameters through command-line arguments.
In my [RGB-LED-Matrix](https://github.com/SimonWaldherr/RGB-LED-Matrix) have added color to the cells to make the simulation more visually appealing. The colors are generated randomly for each cell at the start of the game. Most people are fascinated by the colorful Game of Life, so i decided to rewrite the LED-Matrix code to a pygame version. So everyone can enjoy the colorful Game of Life on their computer.  

If you want to know more about the Game of Life, check out the [Wikipedia page](https://en.wikipedia.org/wiki/Conway%27s_Game_of_Life).  

If you want to know more about the RGB-LED-Matrix, check out the [GitHub page](https://github.com/SimonWaldherr/RGB-LED-Matrix).  

If you want to know more about how to program Conway's Game of Life in various programming languages, check out the [GitHub page](https://github.com/SimonWaldherr/GameOfLife).  

## Requirements
- Python 3.x
- Pygame (`pip install pygame`)
- Pillow (`pip install pillow`)

## Usage

```bash
python rgb_cgol.py [options]
```

### Options
- `-fw`, `--width`: Set the width of the field (default: 128).
- `-fh`, `--height`: Set the height of the field (default: 128).
- `-d`, `--duration`: Set the duration of the game in frames. Use `-1` for an infinite duration (default: -1).
- `-f`, `--fps`: Set the frames per second (default: 20).
- `-o`, `--openfile`: Specify a file to initialize the game state (supports `.png` and `.txt`).
- `-s`, `--cellsize`: Set the size of each cell in pixels (default: 5).
- `--fullscreen`: Run the game in fullscreen mode.

### Examples
1. Run the Game of Life with default parameters:
   ```bash
   python rgb_cgol.py
   ```
2. Run with a 256x256 grid, 10x10 pixel cells, and 60 frames per second:
   ```bash
   python rgb_cgol.py -w 256 --ht 256 -s 10 -f 60
   ```
3. Load an initial state from an image file:
   ```bash
   python rgb_cgol.py -o structures/01.txt
   ```
4. Set the game to run for 500 frames at 30 frames per second:
   ```bash
   python rgb_cgol.py -d 500 -f 30
   ```
5. Run the game in fullscreen mode:
   ```bash
   python rgb_cgol.py --fullscreen
   ```
   - **Note**: When in fullscreen mode, the cell size is automatically adjusted to fit the screen.
   - Press the `ESCAPE` key to exit the game.

## Notes
- If no file is specified with `-o`, a random initial field will be generated.
- The game window will close automatically when the specified duration is reached (if not set to infinite).
- When running in fullscreen, the `cellsize` parameter will be adjusted to fit the screen based on the `width` and `height` specified.
- Press `ESC` to exit the game when in fullscreen mode.

## License
This project is licensed under the MIT License.
