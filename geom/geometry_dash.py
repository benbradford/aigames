import pygame
import math
import random
import os
import glob

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

def load_level(filename):
    print(f"Loading level: {filename}")
    obstacles = []
    finish_line_x = 1000  # Default fallback
    try:
        with open(filename, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    parts = line.split(',')
                    if len(parts) == 5:
                        x, y, width, height, obj_type = parts
                        is_platform = obj_type.strip() == 'green'
                        obstacles.append(Obstacle(int(x), is_platform, int(width), int(y), int(height)))
                    elif len(parts) == 2 and parts[0] == 'FINISH':
                        finish_line_x = int(parts[1])

    except FileNotFoundError:
        pass

    

    return obstacles, finish_line_x

def select_level():
    level_files = glob.glob("level*.txt")
    if not level_files:
        return None
    
    level_files.sort()
    selected_index = 0
    
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Geometry Dash Clone - Select Level")
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 36)
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return None
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected_index = (selected_index - 1) % len(level_files)
                elif event.key == pygame.K_DOWN:
                    selected_index = (selected_index + 1) % len(level_files)
                elif event.key == pygame.K_SPACE:
                    return level_files[selected_index]
        
        # Draw
        screen.fill(BLACK)
        
        # Title
        title = font.render("SELECT LEVEL", True, WHITE)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 100))
        
        # Level list
        for i, level_file in enumerate(level_files):
            color = WHITE if i == selected_index else (128, 128, 128)
            level_text = font.render(f"{i + 1}. {level_file}", True, color)
            y_pos = 200 + i * 50
            screen.blit(level_text, (WIDTH // 2 - level_text.get_width() // 2, y_pos))
            
            # Cursor
            if i == selected_index:
                pygame.draw.rect(screen, WHITE, (WIDTH // 2 - level_text.get_width() // 2 - 20, y_pos, 10, 30))
        
        # Instructions
        instructions = font.render("UP/DOWN to select, SPACE to play", True, WHITE)
        screen.blit(instructions, (WIDTH // 2 - instructions.get_width() // 2, HEIGHT - 100))
        
        pygame.display.flip()
        clock.tick(FPS)
    
    return None

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
        self.space_held = False
        self.jump_power = 0
        
    def start_jump(self):
        if not self.jumping and not self.falling:
            self.jumping = True
            self.jump_time = 0
            self.jump_start_y = self.platform_y if self.on_platform else self.ground_y
            self.space_held = True
            self.jump_power = 15  # Start with minimum jump power
    
    def end_jump(self):
        self.space_held = False
    
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
        
        # Handle space being held for variable jump power
        if self.space_held and self.jumping and self.jump_power < 45:  # Max 45 frames of charging
            self.jump_power += 1
        
        if self.jumping:
            # Sine wave jump effect with variable height
            self.jump_time += 0.08
            if self.jump_time <= math.pi:
                base_height = 120
                height_multiplier = self.jump_power / 30.0  # 0.5x to 1.5x height
                jump_height = math.sin(self.jump_time) * base_height * height_multiplier
                self.y = self.jump_start_y - jump_height
            else:
                self.jumping = False
                self.jump_time = 0
                self.jump_power = 0
                self.space_held = False
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

class FinishLine:
    def __init__(self, x):
        self.x = x
        self.speed = 5  # Same speed as obstacles
    
    def update(self):
        self.x -= self.speed
    
    def draw(self, screen):
        if self.x > -10 and self.x < WIDTH + 10:
            pygame.draw.line(screen, BLUE, (self.x, 0), (self.x, HEIGHT - GROUND_HEIGHT), 5)

class Obstacle:
    def __init__(self, x, is_platform=False, width=OBSTACLE_WIDTH, y=None, height=OBSTACLE_HEIGHT):
        self.x = x
        self.y = y if y is not None else HEIGHT - GROUND_HEIGHT - height
        self.width = width
        self.height = height
        self.speed = 5
        self.is_platform = is_platform
    
    def update(self):
        self.x -= self.speed
    
    def draw(self, screen):
        color = GREEN if self.is_platform else RED
        pygame.draw.rect(screen, color, (self.x, self.y, self.width, self.height))
    
    def collides_with(self, player):
        if not (self.x < player.x + PLAYER_SIZE and 
                self.x + self.width > player.x and
                self.y < player.y + PLAYER_SIZE and
                self.y + self.height > player.y):
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
    while True:
        # Select level
        level_file = select_level()
        if not level_file:
            break
        
        screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption(f"Geometry Dash Clone - {level_file}")
        clock = pygame.time.Clock()
        
        player = Player()
        obstacles, finish_line_x = load_level(level_file)
        finish_line = FinishLine(finish_line_x)
        scroll_x = 0
        
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        player.start_jump()
                elif event.type == pygame.KEYUP:
                    if event.key == pygame.K_SPACE:
                        player.end_jump()
            
            # Update
            player.update(obstacles)
            scroll_x += 3  # Scenery movement speed
            
            # Check finish line - when player crosses it
            if player.x >= finish_line.x:
                running = False
                continue
            
            # Update obstacles and finish line
            finish_line.update()
            for obstacle in obstacles[:]:
                obstacle.update()
                if obstacle.x + obstacle.width < 0:
                    obstacles.remove(obstacle)
                elif obstacle.collides_with(player):
                    running = False
                    break
            
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
            
            # Draw finish line
            finish_line.draw(screen)
            
            player.draw(screen)
            for obstacle in obstacles:
                obstacle.draw(screen)
            
            pygame.display.flip()
            clock.tick(FPS)
    
    pygame.quit()

if __name__ == "__main__":
    main()
