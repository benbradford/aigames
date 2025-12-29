# Space Invaders Game

A feature-rich Space Invaders clone built with Python and Pygame.

## Features

- **5 Difficulty Levels**: From Beginner to Nightmare
- **Multiple Weapon Types**: Split-shot, Laser, and Super Missile powerups
- **Special Alien Types**: 
  - Kamikaze (dives straight down)
  - Shield (takes 3 hits)
  - Zigzag (moves in zigzag pattern)
  - Sniper (shoots accurately at player)
  - Spawner (drops mini-aliens)
- **Destructible Bases**: Provide cover but regenerate over time
- **Endless Gameplay**: New waves spawn every 20 seconds
- **Bonus UFO**: Appears frequently with weapon drops
- **Custom Graphics**: All sprites use custom PNG images
- **Explosion Effects**: Visual feedback when destroying enemies

## Setup Instructions

### Prerequisites

You need Python 3.6 or higher installed on your system.

### Install Pygame

**Option 1 - Using requirements.txt (recommended):**
```bash
pip install -r requirements.txt
```

**Option 2 - Direct install:**
```bash
pip install pygame
```

Or if you're using Python 3 specifically:

```bash
pip3 install pygame
```

### Run the Game

1. Navigate to the space_invaders directory:
```bash
cd space_invaders
```

2. Run the game:
```bash
python space_invaders.py
```

Or:
```bash
python3 space_invaders.py
```

## How to Play

### Controls
- **Arrow Keys**: Move left/right
- **Spacebar**: Shoot
- **1-5 Keys**: Select difficulty on menu screen
- **Q**: Quit from game over screen

### Difficulty Levels
1. **Beginner**: Slow aliens, frequent UFOs, slow wave spawning
2. **Rookie**: Slightly more challenging
3. **Average**: Balanced gameplay
4. **Hard**: Fast aliens, less frequent UFOs
5. **Nightmare**: Maximum challenge

### Scoring
- Regular aliens: 10 points
- Special aliens: 30 points (Shield alien: 50 points)
- Mini-aliens: 5 points
- UFO: 100 points + weapon drop

### Weapons
- **Split-shot** (Yellow drop): Fires 3 bullets at once
- **Laser** (Cyan drop): Pierces through multiple enemies
- **Super Missile** (Orange drop): Large bullets with bigger hit area

## Game Mechanics

- **Bouncing Invaders**: Aliens bounce between top and bottom of screen
- **Base Regeneration**: Defensive bases repair themselves every 5 seconds
- **Wave Spawning**: New alien rows appear every 20 seconds
- **Special Alien Respawning**: Special aliens respawn at top when they fall off bottom
- **Escalating Difficulty**: Remaining aliens become more aggressive

## Files Required

Make sure all these files are in the same directory:
- `space_invaders.py` - Main game file
- `player.png` - Player ship sprite
- `invader.png` - Regular alien sprite
- `ufo.png` - UFO sprite
- `exp.png` - Explosion effect
- `kamikaze.png` - Kamikaze alien sprite
- `shield.png` - Shield alien sprite
- `zigzag.png` - Zigzag alien sprite
- `sniper.png` - Sniper alien sprite
- `spawner.png` - Spawner alien sprite
- `mini.png` - Mini-alien sprite

## Troubleshooting

### ModuleNotFoundError: No module named 'pygame'

If you get this error, pygame is not installed. Try these solutions:

**Option 1 - Using requirements.txt:**
```bash
pip install -r requirements.txt
```

**Option 2 - Basic install:**
```bash
pip install pygame
```

**Option 3 - If you have multiple Python versions:**
```bash
pip3 install -r requirements.txt
```

**Option 4 - If pip is not recognized:**
```bash
python -m pip install -r requirements.txt
```

**Option 5 - For macOS users:**
```bash
python3 -m pip install -r requirements.txt
```

**Option 6 - Upgrade pip first:**
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**Option 7 - Using virtual environment (recommended):**
```bash
python3 -m venv path/to/venv
source path/to/venv/bin/activate
python3 -m pip install -r requirements.txt
```

### Other Issues

If images don't load, make sure all PNG files are in the same directory as the Python script.

## Enjoy the Game!

Try to achieve the highest score possible in this endless space battle!
