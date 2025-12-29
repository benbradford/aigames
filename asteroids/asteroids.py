import pygame
import random
import math

pygame.init()

# Display
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Asteroids")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
MAGENTA = (255, 0, 255)

FPS = 60
clock = pygame.time.Clock()

# Game settings
SPACESHIP_ACCELERATION = 0.12
SPACESHIP_FRICTION = 0.98
LASER_SPEED = 12
ASTEROID_SPEED = 2.5
LIVES = 3
font = pygame.font.SysFont('Arial', 28)

# Helper function
def distance(x1, y1, x2, y2):
    return math.hypot(x2 - x1, y2 - y1)

# Spaceship class
class Spaceship:
    def __init__(self, width=30, height=30):
        self.width = width
        self.height = height
        self.reset()

    def reset(self):
        self.x = WIDTH // 2
        self.y = HEIGHT // 2
        self.angle = 90
        self.velocity_x = 0
        self.velocity_y = 0
        self.invincible = False
        self.state = "alive"  # can be 'alive', 'respawning'
        self.respawn_timer = 0
        self.invincibility_timer = 0

    def start_respawn(self):
        self.state = "respawning"
        self.respawn_timer = FPS  # 1 second countdown
        self.invincible = True
        self.invincibility_timer = 120  # 2 seconds invincibility

    def move(self, keys, difficulty_level):
        if self.state != "alive":
            return  # Prevent moving while respawning

        # Rotation
        if keys[pygame.K_LEFT]:
            self.angle += 5
        if keys[pygame.K_RIGHT]:
            self.angle -= 5

        # Movement (forward) logic
        if difficulty_level == "extreme":
            # In Extreme mode, always move forward in the direction of the spaceship's angle
            self.velocity_x += math.cos(math.radians(self.angle)) * SPACESHIP_ACCELERATION
            self.velocity_y -= math.sin(math.radians(self.angle)) * SPACESHIP_ACCELERATION
        else:
            if keys[pygame.K_UP]:
                self.velocity_x += math.cos(math.radians(self.angle)) * SPACESHIP_ACCELERATION
                self.velocity_y -= math.sin(math.radians(self.angle)) * SPACESHIP_ACCELERATION

        # Apply friction
        self.velocity_x *= SPACESHIP_FRICTION
        self.velocity_y *= SPACESHIP_FRICTION

        # Update position
        self.x += self.velocity_x
        self.y += self.velocity_y

        # Wrap around the screen if out of bounds
        if self.x < 0: self.x = WIDTH
        elif self.x > WIDTH: self.x = 0
        if self.y < 0: self.y = HEIGHT
        elif self.y > HEIGHT: self.y = 0

    def update(self):
        if self.state == "respawning":
            self.respawn_timer -= 1
            self.invincibility_timer -= 1
            if self.respawn_timer <= 0:
                self.state = "alive"
            if self.invincibility_timer <= 0:
                self.invincible = False

    def draw(self, surface):
        half_base = self.width / 2
        points = [
            (self.x + math.cos(math.radians(self.angle)) * self.height,
             self.y - math.sin(math.radians(self.angle)) * self.height),
            (self.x + math.cos(math.radians(self.angle + 120)) * half_base,
             self.y - math.sin(math.radians(self.angle + 120)) * half_base),
            (self.x + math.cos(math.radians(self.angle - 120)) * half_base,
             self.y - math.sin(math.radians(self.angle - 120)) * half_base)
        ]
        if self.invincible and self.state == "respawning":
            if self.invincibility_timer % 10 < 5:
                pygame.draw.polygon(surface, MAGENTA, points)  # Flashing during respawn
        elif self.state != "respawning":
            pygame.draw.polygon(surface, WHITE, points)

        # Show countdown number when respawning
        if self.state == "respawning":
            countdown_text = font.render(str(self.get_countdown_number()), True, WHITE)
            surface.blit(countdown_text, (WIDTH // 2 - countdown_text.get_width() // 2, HEIGHT // 2))

    def get_countdown_number(self):
        if self.state == "respawning":
            return max(1, int(self.respawn_timer * 3 / FPS))
        return 0

# Laser class
class Laser:
    def __init__(self, x, y, angle):
        self.x = x
        self.y = y
        self.angle = angle
        self.width = 6
        self.height = 14
        self.image = pygame.Surface((self.width, self.height))
        self.image.fill(RED)
        self.rect = self.image.get_rect(center=(x, y))
        self.velocity = LASER_SPEED

    def update(self):
        self.x += math.cos(math.radians(self.angle)) * self.velocity
        self.y -= math.sin(math.radians(self.angle)) * self.velocity
        self.rect.center = (self.x, self.y)

    def off_screen(self):
        return self.x < 0 or self.x > WIDTH or self.y < 0 or self.y > HEIGHT

# Asteroid class
class Asteroid:
    def __init__(self, size=None, x=None, y=None, split=False):
        self.size = size if size else random.randint(30, 40)
        self.split = split
        self.speed = ASTEROID_SPEED * (self.size / 40)
        self.angle = random.randint(0, 360)
        self.points = []
        num_vertices = random.randint(6, 10)
        for i in range(num_vertices):
            angle = i * (360 / num_vertices)
            radius = self.size // 2 + random.randint(-self.size // 4, self.size // 4)
            rad_angle = math.radians(angle)
            px = math.cos(rad_angle) * radius
            py = math.sin(rad_angle) * radius
            self.points.append((px, py))

        # Random position for asteroids
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, HEIGHT)
        self.rect = pygame.Rect(self.x - self.size // 2, self.y - self.size // 2, self.size, self.size)

    def move(self):
        self.x += math.cos(math.radians(self.angle)) * self.speed
        self.y += math.sin(math.radians(self.angle)) * self.speed
        if self.x < 0: self.x = WIDTH
        elif self.x > WIDTH: self.x = 0
        if self.y < 0: self.y = HEIGHT
        elif self.y > HEIGHT: self.y = 0
        self.rect.center = (self.x, self.y)

    def update(self):
        self.move()

    def draw(self, surface):
        moved_points = [(self.x + px, self.y + py) for px, py in self.points]
        pygame.draw.polygon(surface, GREEN, moved_points)

# Difficulty selection start screen
def start_screen():
    global ASTEROID_SPEED
    global asteroids
    global difficulty_level

    waiting = True
    while waiting:
        screen.fill(BLACK)
        title_text = font.render("Asteroids", True, WHITE)
        easy_text = font.render("Easy (1)", True, WHITE)
        normal_text = font.render("Normal (2)", True, WHITE)
        hard_text = font.render("Hard (3)", True, WHITE)
        extreme_text = font.render("Extreme (4)", True, WHITE)
        quit_text = font.render("Press Q to Quit", True, WHITE)

        screen.blit(title_text, (WIDTH//2 - title_text.get_width()//2, HEIGHT//2 - 100))
        screen.blit(easy_text, (WIDTH//2 - easy_text.get_width()//2, HEIGHT//2))
        screen.blit(normal_text, (WIDTH//2 - normal_text.get_width()//2, HEIGHT//2 + 50))
        screen.blit(hard_text, (WIDTH//2 - hard_text.get_width()//2, HEIGHT//2 + 100))
        screen.blit(extreme_text, (WIDTH//2 - extreme_text.get_width()//2, HEIGHT//2 + 150))
        screen.blit(quit_text, (WIDTH//2 - quit_text.get_width()//2, HEIGHT//2 + 200))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:  # Easy
                    difficulty_level = "easy"
                    ASTEROID_SPEED = 2
                    asteroids = [Asteroid() for _ in range(4)]
                    return
                elif event.key == pygame.K_2:  # Normal
                    difficulty_level = "normal"
                    ASTEROID_SPEED = 3
                    asteroids = [Asteroid() for _ in range(6)]
                    return
                elif event.key == pygame.K_3:  # Hard
                    difficulty_level = "hard"
                    ASTEROID_SPEED = 4
                    asteroids = [Asteroid() for _ in range(8)]
                    return
                elif event.key == pygame.K_4:  # Extreme
                    difficulty_level = "extreme"
                    ASTEROID_SPEED = 4
                    asteroids = [Asteroid() for _ in range(8)]
                    return
                elif event.key == pygame.K_q:  # Quit
                    pygame.quit()
                    exit()

# End screen function
def end_screen(final_score, win=False):
    waiting = True
    while waiting:
        screen.fill(BLACK)
        go_text = font.render("You Win!" if win else "Game Over", True, WHITE)
        exit_text = font.render("Press Space to Exit", True, WHITE)
        score_text = font.render(f"Score: {final_score}", True, WHITE)
        screen.blit(go_text, (WIDTH//2 - go_text.get_width()//2, HEIGHT//2 - 70))
        screen.blit(score_text, (WIDTH//2 - score_text.get_width()//2, HEIGHT//2 - 20))
        screen.blit(exit_text, (WIDTH//2 - exit_text.get_width()//2, HEIGHT//2 + 30))
        pygame.display.flip()
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                pygame.quit()
                exit()

# Setup
difficulty_level = "normal"  # default to normal
start_screen()

spaceship = Spaceship()
lasers = []
score = 0
lives = LIVES
space_released = True

# Main game loop
running = True
while running:
    keys = pygame.key.get_pressed()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

    screen.fill(BLACK)
    spaceship.move(keys, difficulty_level)
    spaceship.update()

    # Shooting
    if keys[pygame.K_SPACE] and space_released and spaceship.state == "alive":
        lasers.append(Laser(spaceship.x, spaceship.y, spaceship.angle))
        space_released = False
    if not keys[pygame.K_SPACE]:
        space_released = True

    # Collision with asteroids (only if the spaceship is alive)
    if spaceship.state == "alive":
        for asteroid in asteroids:
            if spaceship.x + spaceship.width // 2 > asteroid.rect.left and spaceship.x - spaceship.width // 2 < asteroid.rect.right:
                if spaceship.y + spaceship.height // 2 > asteroid.rect.top and spaceship.y - spaceship.height // 2 < asteroid.rect.bottom:
                    lives -= 1
                    if lives <= 0:
                        end_screen(score, win=False)
                    else:
                        spaceship.start_respawn()
                    break

    # Lasers vs asteroids
    lasers_to_remove = []
    asteroids_to_remove = set()
    new_asteroids = []
    for laser in lasers:
        laser.update()
        if laser.off_screen():
            lasers_to_remove.append(laser)
        for asteroid in asteroids:
            if laser.rect.colliderect(asteroid.rect):
                lasers_to_remove.append(laser)
                asteroids_to_remove.add(asteroid)
                score += 10
                if not asteroid.split and asteroid.size > 15:
                    new_size = asteroid.size // 2
                    for _ in range(2):
                        new_asteroids.append(Asteroid(size=new_size, x=asteroid.x, y=asteroid.y, split=True))

    for laser in lasers_to_remove:
        if laser in lasers:
            lasers.remove(laser)
    for asteroid in asteroids_to_remove:
        if asteroid in asteroids:
            asteroids.remove(asteroid)
    asteroids.extend(new_asteroids)

    # Draw objects
    spaceship.draw(screen)  # Always draw spaceship
    for laser in lasers:
        screen.blit(laser.image, laser.rect)
    for asteroid in asteroids:
        asteroid.update()  # Update asteroid movement
        asteroid.draw(screen)

    # Score & lives
    screen.blit(font.render(f"Score: {score}", True, WHITE), (10, 10))
    screen.blit(font.render(f"Lives: {lives}", True, WHITE), (10, 40))

    # Win condition
    if len(asteroids) == 0:
        end_screen(score, win=True)

    pygame.display.flip()
    clock.tick(FPS)
