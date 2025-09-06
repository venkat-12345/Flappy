# Flappy Bird NEAT AI

This project is a Flappy Bird clone built with Python and Pygame, featuring both manual play and an AI agent trained using NEAT (NeuroEvolution of Augmenting Topologies).

## Features

- Play Flappy Bird manually ([game.py](game.py))
- Train an AI to play Flappy Bird using NEAT ([neat_train.py](neat_train.py))
- High score tracking for both manual and AI modes
- Fullscreen graphics with custom assets

## Files

- `game.py`: Main game loop for manual play
- `neat_train.py`: NEAT training and evaluation for AI agent
- `config-feedforward.txt`: NEAT configuration file
- `bird.png`, `pipe.png`, `pipe.jfif`, `ground.png`: Game assets
- `high_score.txt`, `neat_highscore.txt`: High score storage
- `gueessthebymne.py`: Simple number guessing game (unrelated demo)

## Requirements

- Python 3.x
- Pygame
- NEAT-Python (`pip install neat-python`)

## How to Play

### Manual Mode

```sh
python [game.py](http://_vscodecontentref_/0)s