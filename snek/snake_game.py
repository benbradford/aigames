import pygame
import random
import sys

pygame.init()

# Constants
WIDTH, HEIGHT = 600, 600
CELL_SIZE = 20
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake Game")
clock = pygame.time.Clock()

# Snake initial position and direction
snake = [(WIDTH//2, HEIGHT//2)]
direction = (CELL_SIZE, 0)

# Apple position
apple = (random.randint(0, WIDTH//CELL_SIZE-1) * CELL_SIZE,
         random.randint(0, HEIGHT//CELL_SIZE-1) * CELL_SIZE)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and direction != (0, CELL_SIZE):
                direction = (0, -CELL_SIZE)
            elif event.key == pygame.K_DOWN and direction != (0, -CELL_SIZE):
                direction = (0, CELL_SIZE)
            elif event.key == pygame.K_LEFT and direction != (CELL_SIZE, 0):
                direction = (-CELL_SIZE, 0)
            elif event.key == pygame.K_RIGHT and direction != (-CELL_SIZE, 0):
                direction = (CELL_SIZE, 0)

    # Move snake
    head = (snake[0][0] + direction[0], snake[0][1] + direction[1])
    
    # Check wall collision
    if head[0] < 0 or head[0] >= WIDTH or head[1] < 0 or head[1] >= HEIGHT:
        pygame.quit()
        sys.exit()
    
    # Check self collision
    if head in snake:
        pygame.quit()
        sys.exit()
    
    snake.insert(0, head)
    
    # Check apple collision
    if head == apple:
        apple = (random.randint(0, WIDTH//CELL_SIZE-1) * CELL_SIZE,
                 random.randint(0, HEIGHT//CELL_SIZE-1) * CELL_SIZE)
    else:
        snake.pop()
    
    # Draw everything
    screen.fill(BLACK)
    for segment in snake:
        pygame.draw.rect(screen, GREEN, (segment[0], segment[1], CELL_SIZE, CELL_SIZE))
    pygame.draw.rect(screen, RED, (apple[0], apple[1], CELL_SIZE, CELL_SIZE))
    
    pygame.display.flip()
    clock.tick(10)
