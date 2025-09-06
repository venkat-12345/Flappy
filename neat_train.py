# neat_train.py
import os, random, sys, pygame, neat

from game import SCREEN_WIDTH, SCREEN_HEIGHT, PIPE_IMG, GROUND_IMG, BIRD_IMG, WHITE, BLACK, gravity

pygame.font.init()
STAT_FONT = pygame.font.SysFont("comicsans", 40)

# ========== Pipe creation & drawing ==========
def create_pipe():
    gap_size = int(SCREEN_HEIGHT * 0.25)
    gap_y = random.randint(int(SCREEN_HEIGHT * 0.2), int(SCREEN_HEIGHT * 0.8) - gap_size)
    return {
        'x': SCREEN_WIDTH,
        'top_y': gap_y - PIPE_IMG.get_height(),
        'bottom_y': gap_y + gap_size,
        'scored': False
    }

def draw_pipes(screen, pipes):
    for pipe in pipes:
        flipped = pygame.transform.flip(PIPE_IMG, False, True)
        screen.blit(flipped, (pipe['x'], pipe['top_y']))
        screen.blit(PIPE_IMG, (pipe['x'], pipe['bottom_y']))

def check_collision(bird_x, bird_y, pipes):
    bird_rect = pygame.Rect(bird_x, bird_y, BIRD_IMG.get_width(), BIRD_IMG.get_height())
    if bird_y < 0 or bird_y + BIRD_IMG.get_height() > SCREEN_HEIGHT - GROUND_IMG.get_height():
        return True
    for pipe in pipes:
        top = pygame.Rect(pipe['x'], pipe['top_y'], PIPE_IMG.get_width(), PIPE_IMG.get_height())
        bottom = pygame.Rect(pipe['x'], pipe['bottom_y'], PIPE_IMG.get_width(), PIPE_IMG.get_height())
        if bird_rect.colliderect(top) or bird_rect.colliderect(bottom):
            return True
    return False


# ========== NEAT evaluation ==========
GEN = 0
HIGH_SCORE_FILE = "neat_highscore.txt"

def load_high_score():
    if os.path.exists(HIGH_SCORE_FILE):
        with open(HIGH_SCORE_FILE, "r") as f:
            try:
                return int(f.read().strip())
            except:
                return 0
    return 0

def save_high_score(score):
    with open(HIGH_SCORE_FILE, "w") as f:
        f.write(str(score))

HIGH_SCORE = load_high_score()   # Load at startup


def eval_genomes(genomes, config):
    global GEN, HIGH_SCORE
    GEN += 1

    nets, ge, birds = [], [], []
    for _, genome in genomes:
        genome.fitness = 0
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        nets.append(net)
        birds.append({'x': int(SCREEN_WIDTH*0.1), 'y': SCREEN_HEIGHT//2, 'velocity': 0})
        ge.append(genome)

    pipes = [create_pipe()]
    score = 0
    clock = pygame.time.Clock()
    pipe_timer = 0
    run = True
    base_speed = 30

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)

    while run and birds:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                pygame.quit(); sys.exit()

        # ========== Move Pipes ==========
        
        speed = base_speed + score // 5   # speed increases every 5 points
        for pipe in pipes:
            pipe['x'] -= speed
        pipe_timer += 1

        if pipe_timer > max(90 - score*2, 100):  # spawn faster as score increases, min cap
            pipes.append(create_pipe())
            pipe_timer = 0
        pipes[:] = [p for p in pipes if p['x'] + PIPE_IMG.get_width() > 0]

        # ========== Update Birds ==========
        for i, bird in enumerate(birds):
            bird['velocity'] += gravity
            bird['y'] += bird['velocity']

            # pick nearest pipe
            nearest_pipe = None
            for p in pipes:
                if p['x'] + PIPE_IMG.get_width() > bird['x']:
                    nearest_pipe = p
                    break

            if nearest_pipe:
                output = nets[i].activate((
                    bird['y'],
                    bird['velocity'],
                    nearest_pipe['x'] - bird['x'],
                    nearest_pipe['bottom_y']
                ))
                if output[0] > 0.5:
                    bird['velocity'] = -8

            # Fitness reward
            ge[i].fitness += 0.1

        # ========== Scoring ==========
        for pipe in pipes:
            if not pipe['scored'] and pipe['x'] + PIPE_IMG.get_width() < birds[0]['x']:
                pipe['scored'] = True
                score += 1
                if score > HIGH_SCORE:
                    HIGH_SCORE = score
                    save_high_score(HIGH_SCORE)
                for g in ge:
                    g.fitness += 10  # reward all alive birds

        # ========== Collision Check ==========
        for i in range(len(birds)-1, -1, -1):
            if check_collision(birds[i]['x'], birds[i]['y'], pipes):
                ge[i].fitness -= 1
                birds.pop(i); nets.pop(i); ge.pop(i)

        # ========== Draw Everything ==========
        screen.fill(WHITE)
        for bird in birds:
            screen.blit(BIRD_IMG, (bird['x'], bird['y']))
        draw_pipes(screen, pipes)
        screen.blit(GROUND_IMG, (0, SCREEN_HEIGHT - GROUND_IMG.get_height()))

        # Stats
        screen.blit(STAT_FONT.render(f"Score: {score}", 1, BLACK), (10, 10))
        screen.blit(STAT_FONT.render(f"High Score: {HIGH_SCORE}", 1, BLACK), (10, 50))
        screen.blit(STAT_FONT.render(f"Gen: {GEN}", 1, BLACK), (10, 90))
        screen.blit(STAT_FONT.render(f"Alive: {len(birds)}", 1, BLACK), (10, 130))

        pygame.display.update()
        clock.tick(30)


# ========== NEAT Runner ==========
def run_neat(config_file):
    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_file)
    p = neat.Population(config)
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    winner = p.run(eval_genomes, 50)
    print("\nBest genome:\n", winner)


if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "config-feedforward.txt")
    run_neat(config_path)
