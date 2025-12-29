import pygame
import math
import random

pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
FPS = 60
GROUND_HEIGHT = 100
PLAYER_SIZE = 30
OBSTACLE_WIDTH = 20
OBSTACLE_HEIGHT = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 100, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

class Player:
    def __init__(self):
        self.x = 150
        self.y = HEIGHT - GROUND_HEIGHT - PLAYER_SIZE
        self.ground_y = self.y
        self.vel_y = 0
        self.jumping = False
        self.jump_time = 0
        self.on_platform = False
        self.platform_y = self.ground_y
        self.falling = False
        self.jump_start_y = self.ground_y
        
    def jump(self):
        if not self.jumping and not self.falling:
            self.jumping = True
            self.jump_time = 0
            self.jump_start_y = self.platform_y if self.on_platform else self.ground_y
    
    def update(self, obstacles):
        # Check if on platform
        was_on_platform = self.on_platform
        self.on_platform = False
        for obstacle in obstacles:
            if obstacle.is_on_top(self):
                self.on_platform = True
                self.platform_y = obstacle.y - PLAYER_SIZE
                # End jump cycle if landing on platform
                if self.jumping and self.jump_time > math.pi / 2:
                    self.jumping = False
                if self.falling:
                    self.falling = False
                    self.vel_y = 0
                break
        
        # Start falling if left platform
        if was_on_platform and not self.on_platform and not self.jumping:
            self.falling = True
            self.vel_y = 0
        
        if not self.on_platform:
            self.platform_y = self.ground_y
        
        if self.jumping:
            # Sine wave jump effect
            self.jump_time += 0.08
            if self.jump_time <= math.pi:
                jump_height = math.sin(self.jump_time) * 120
                self.y = self.jump_start_y - jump_height
            else:
                self.jumping = False
                self.jump_time = 0
                # Start falling if not on a platform, maintaining downward velocity
                if not self.on_platform:
                    self.falling = True
                    # Calculate velocity based on jump descent speed
                    self.vel_y = 0.08 * 120 * math.cos(math.pi) * -1  # Approximate descent velocity
                else:
                    self.y = self.platform_y
        elif self.falling:
            # Gradual fall with gravity
            self.vel_y += 0.5
            self.y += self.vel_y
            if self.y >= self.ground_y:
                self.y = self.ground_y
                self.falling = False
                self.vel_y = 0
        else:
            self.y = self.platform_y if self.on_platform else self.ground_y
    
    def draw(self, screen):
        pygame.draw.rect(screen, BLUE, (self.x, self.y, PLAYER_SIZE, PLAYER_SIZE))

class Obstacle:
    def __init__(self, x, is_platform=False, width=OBSTACLE_WIDTH):
        self.x = x
        self.y = HEIGHT - GROUND_HEIGHT - OBSTACLE_HEIGHT
        self.width = width
        self.speed = 5
        self.is_platform = is_platform
    
    def update(self):
        self.x -= self.speed
    
    def draw(self, screen):
        color = GREEN if self.is_platform else RED
        pygame.draw.rect(screen, color, (self.x, self.y, self.width, OBSTACLE_HEIGHT))
    
    def collides_with(self, player):
        if not (self.x < player.x + PLAYER_SIZE and 
                self.x + self.width > player.x and
                self.y < player.y + PLAYER_SIZE and
                self.y + OBSTACLE_HEIGHT > player.y):
            return False
        
        if self.is_platform:
            # Don't kill if player is on top of platform
            if self.is_on_top(player):
                return False
            # Only kill if hitting from the side
            return True
        return True
    
    def is_on_top(self, player):
        return (self.is_platform and 
                self.x < player.x + PLAYER_SIZE and 
                self.x + self.width > player.x and
                player.y + PLAYER_SIZE >= self.y - 15 and
                player.y <= self.y + 5)

def main():
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Geometry Dash Clone")
    clock = pygame.time.Clock()
    
    player = Player()
    obstacles = []
    scroll_x = 0
    spawn_timer = 0
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    player.jump()
        
        # Update
        player.update(obstacles)
        scroll_x += 3  # Scenery movement speed
        
        # Update obstacles and check collisions
        for obstacle in obstacles[:]:
            obstacle.update()
            if obstacle.x + obstacle.width < 0:
                obstacles.remove(obstacle)
            elif obstacle.collides_with(player):
                print("Game Over!")
                running = False
        
        # Spawn obstacles
        spawn_timer += 1
        if spawn_timer > random.randint(60, 120):  # Random spawn interval
            if random.choice([True, False]):  # 50% chance for platform
                width = random.choice([OBSTACLE_WIDTH, 80, 120])  # Varying platform widths
                obstacles.append(Obstacle(WIDTH, True, width))
            else:
                obstacles.append(Obstacle(WIDTH, False))
            spawn_timer = 0
        
        # Draw
        screen.fill(BLACK)
        
        # Draw ground with scrolling effect
        ground_segments = WIDTH // 50 + 2
        for i in range(ground_segments):
            x = (i * 50 - scroll_x % 50)
            pygame.draw.rect(screen, GREEN, (x, HEIGHT - GROUND_HEIGHT, 50, GROUND_HEIGHT))
            pygame.draw.line(screen, WHITE, (x, HEIGHT - GROUND_HEIGHT), (x + 50, HEIGHT - GROUND_HEIGHT), 2)
        
        # Draw background lines for movement effect
        for i in range(0, WIDTH + 100, 100):
            x = i - (scroll_x % 100)
            pygame.draw.line(screen, (50, 50, 50), (x, 0), (x, HEIGHT - GROUND_HEIGHT), 1)
        
        player.draw(screen)
        for obstacle in obstacles:
            obstacle.draw(screen)
        
        pygame.display.flip()
        clock.tick(FPS)
    
    pygame.quit()

if __name__ == "__main__":
    main()
