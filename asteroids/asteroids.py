import pygame
import math
import random

pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Asteroids")
clock = pygame.time.Clock()

class Ship:
    def __init__(self):
        self.x = WIDTH // 2
        self.y = HEIGHT // 2
        self.angle = 0
        self.vel_x = 0
        self.vel_y = 0
        self.thrust = 0
        self.size = 10
        
    def update(self, keys):
        if keys[pygame.K_LEFT]:
            self.angle -= 5
        if keys[pygame.K_RIGHT]:
            self.angle += 5
        if keys[pygame.K_UP]:
            self.thrust = 0.15
        else:
            self.thrust *= 0.95
            
        self.vel_x += math.cos(math.radians(self.angle)) * self.thrust
        self.vel_y += math.sin(math.radians(self.angle)) * self.thrust
        self.vel_x *= 0.98
        self.vel_y *= 0.98
        
        self.x += self.vel_x
        self.y += self.vel_y
        
        self.x %= WIDTH
        self.y %= HEIGHT
        
    def draw(self, screen):
        points = []
        for angle_offset, distance in [(0, self.size), (140, self.size//2), (220, self.size//2)]:
            angle = math.radians(self.angle + angle_offset)
            px = self.x + math.cos(angle) * distance
            py = self.y + math.sin(angle) * distance
            points.append((px, py))
        pygame.draw.polygon(screen, (255, 255, 255), points)

class Bullet:
    def __init__(self, x, y, angle):
        self.x = x
        self.y = y
        self.vel_x = math.cos(math.radians(angle)) * 8
        self.vel_y = math.sin(math.radians(angle)) * 8
        self.life = 60
        
    def update(self):
        self.x += self.vel_x
        self.y += self.vel_y
        self.x %= WIDTH
        self.y %= HEIGHT
        self.life -= 1
        return self.life > 0
        
    def draw(self, screen):
        pygame.draw.circle(screen, (255, 255, 255), (int(self.x), int(self.y)), 2)

class Asteroid:
    def __init__(self, x, y, size):
        self.x = x
        self.y = y
        self.size = size
        self.vel_x = random.uniform(-2, 2)
        self.vel_y = random.uniform(-2, 2)
        self.angle = 0
        self.rotation = random.uniform(-5, 5)
        
    def update(self):
        self.x += self.vel_x
        self.y += self.vel_y
        self.x %= WIDTH
        self.y %= HEIGHT
        self.angle += self.rotation
        
    def draw(self, screen):
        points = []
        for i in range(8):
            angle = math.radians(i * 45 + self.angle)
            radius = self.size + random.uniform(-3, 3)
            px = self.x + math.cos(angle) * radius
            py = self.y + math.sin(angle) * radius
            points.append((px, py))
        pygame.draw.polygon(screen, (255, 255, 255), points, 2)
        
    def collides_with(self, other_x, other_y, other_size):
        dx = self.x - other_x
        dy = self.y - other_y
        distance = math.sqrt(dx*dx + dy*dy)
        return distance < self.size + other_size

def spawn_asteroid():
    side = random.randint(0, 3)
    if side == 0:  # top
        return Asteroid(random.randint(0, WIDTH), -50, 30)
    elif side == 1:  # right
        return Asteroid(WIDTH + 50, random.randint(0, HEIGHT), 30)
    elif side == 2:  # bottom
        return Asteroid(random.randint(0, WIDTH), HEIGHT + 50, 30)
    else:  # left
        return Asteroid(-50, random.randint(0, HEIGHT), 30)

ship = Ship()
bullets = []
asteroids = []
lives = 3
score = 0
font = pygame.font.Font(None, 36)

for _ in range(5):
    asteroids.append(spawn_asteroid())

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                bullets.append(Bullet(ship.x, ship.y, ship.angle))
            elif event.key == pygame.K_q and lives <= 0:
                running = False
    
    keys = pygame.key.get_pressed()
    ship.update(keys)
    
    bullets = [bullet for bullet in bullets if bullet.update()]
    
    for asteroid in asteroids:
        asteroid.update()
    
    # Check bullet-asteroid collisions
    for bullet in bullets[:]:
        for asteroid in asteroids[:]:
            if asteroid.collides_with(bullet.x, bullet.y, 2):
                bullets.remove(bullet)
                asteroids.remove(asteroid)
                score += 10
                
                if asteroid.size > 10:
                    for _ in range(2):
                        new_asteroid = Asteroid(asteroid.x, asteroid.y, asteroid.size // 2)
                        asteroids.append(new_asteroid)
                break
    
    # Check ship-asteroid collisions
    for asteroid in asteroids:
        if asteroid.collides_with(ship.x, ship.y, ship.size):
            lives -= 1
            ship.x = WIDTH // 2
            ship.y = HEIGHT // 2
            ship.vel_x = ship.vel_y = 0
            break
    
    # Spawn new asteroids
    if len(asteroids) < 5:
        asteroids.append(spawn_asteroid())
    
    screen.fill((0, 0, 0))
    ship.draw(screen)
    
    for bullet in bullets:
        bullet.draw(screen)
    
    for asteroid in asteroids:
        asteroid.draw(screen)
    
    lives_text = font.render(f"Lives: {lives}", True, (255, 255, 255))
    score_text = font.render(f"Score: {score}", True, (255, 255, 255))
    screen.blit(lives_text, (10, 10))
    screen.blit(score_text, (10, 50))
    
    if lives <= 0:
        game_over_text = font.render("GAME OVER", True, (255, 255, 255))
        quit_text = font.render("Press Q to quit", True, (255, 255, 255))
        screen.blit(game_over_text, (WIDTH//2 - 80, HEIGHT//2))
        screen.blit(quit_text, (WIDTH//2 - 90, HEIGHT//2 + 40))
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
