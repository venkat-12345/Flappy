# game.py
import pygame
import random
import sys
import os
from pygame.locals import *

pygame.init()

# === Constants ===
info = pygame.display.Info()
SCREEN_WIDTH, SCREEN_HEIGHT = info.current_w, info.current_h
FPS = 60
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
gravity = 0.5
current_dir = os.path.dirname(__file__)

# === Assets ===
BIRD_IMG = pygame.image.load(os.path.join(current_dir, 'bird.png'))
PIPE_IMG = pygame.image.load(os.path.join(current_dir, 'pipe.jfif'))
GROUND_IMG = pygame.image.load(os.path.join(current_dir, 'ground.png'))

BIRD_IMG = pygame.transform.scale(BIRD_IMG, (int(SCREEN_WIDTH*0.05), int(SCREEN_HEIGHT*0.05)))
PIPE_IMG = pygame.transform.scale(PIPE_IMG, (int(SCREEN_WIDTH*0.055), int(SCREEN_HEIGHT*0.7)))
GROUND_IMG = pygame.transform.scale(GROUND_IMG, (SCREEN_WIDTH, int(SCREEN_HEIGHT*0.15)))

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("Flappy Bird")

# === Game State ===
bird_x = int(SCREEN_WIDTH*0.1)
bird_y = SCREEN_HEIGHT//2
bird_velocity = 0
pipes = []
score = 0
current_speed = 5

def create_pipe():
    gap_size = int(SCREEN_HEIGHT*0.25)
    gap_y = random.randint(int(SCREEN_HEIGHT*0.2), int(SCREEN_HEIGHT*0.8) - gap_size)
    return {'x': SCREEN_WIDTH, 'top_y': gap_y - PIPE_IMG.get_height(),
            'bottom_y': gap_y + gap_size, 'scored': False}

def draw_pipes():
    for pipe in pipes:
        flipped = pygame.transform.flip(PIPE_IMG, False, True)
        screen.blit(flipped, (pipe['x'], pipe['top_y']))
        screen.blit(PIPE_IMG, (pipe['x'], pipe['bottom_y']))

def move_pipes():
    global score, current_speed
    for pipe in pipes:
        pipe['x'] -= current_speed * (SCREEN_WIDTH/1000)
        if not pipe['scored'] and pipe['x'] + PIPE_IMG.get_width() <= bird_x:
            pipe['scored'] = True
            score += 1
            current_speed = 5 + score*0.1
    pipes[:] = [p for p in pipes if p['x'] + PIPE_IMG.get_width() > 0]

def check_collision():
    bird_rect = pygame.Rect(bird_x, bird_y, BIRD_IMG.get_width(), BIRD_IMG.get_height())
    if bird_y < 0 or bird_y + BIRD_IMG.get_height() > SCREEN_HEIGHT - GROUND_IMG.get_height():
        return True
    for pipe in pipes:
        top = pygame.Rect(pipe['x'], pipe['top_y'], PIPE_IMG.get_width(), PIPE_IMG.get_height())
        bottom = pygame.Rect(pipe['x'], pipe['bottom_y'], PIPE_IMG.get_width(), PIPE_IMG.get_height())
        if bird_rect.colliderect(top) or bird_rect.colliderect(bottom):
            return True
    return False

def draw_game():
    screen.fill(WHITE)
    screen.blit(BIRD_IMG, (bird_x, bird_y))
    draw_pipes()
    screen.blit(GROUND_IMG, (0, SCREEN_HEIGHT - GROUND_IMG.get_height()))
    font = pygame.font.Font(None, 36)
    screen.blit(font.render(f"Score: {score}", True, BLACK), (10, 10))
    pygame.display.update()

def main():
    global bird_y, bird_velocity, pipes, score, current_speed
    clock = pygame.time.Clock()
    pipes = []
    score = 0
    current_speed = 5
    bird_y = SCREEN_HEIGHT//2
    bird_velocity = 0
    pipe_timer = 0

    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE: pygame.quit(); sys.exit()
                if e.key == pygame.K_SPACE: bird_velocity = -10

        bird_velocity += gravity
        bird_y += bird_velocity

        if check_collision():  # Reset on crash
            pipes = [create_pipe()]
            score = 0
            bird_y = SCREEN_HEIGHT//2
            bird_velocity = 0
            current_speed = 5

        pipe_timer += 1
        if pipe_timer > 90:
            pipes.append(create_pipe())
            pipe_timer = 0

        move_pipes()
        draw_game()
        clock.tick(30)

if __name__ == "__main__":
    main()
