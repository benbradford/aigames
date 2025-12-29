import pygame
import random

pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Invaders")
clock = pygame.time.Clock()

# Load images
player_img = pygame.image.load("player.png")
player_img = pygame.transform.scale(player_img, (30, 20))
invader_img = pygame.image.load("invader.png")
invader_img = pygame.transform.scale(invader_img, (30, 20))
ufo_img = pygame.image.load("ufo.png")
ufo_img = pygame.transform.scale(ufo_img, (40, 15))

# Colors
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLACK = (0, 0, 0)

# Player
player_x = WIDTH // 2
player_y = HEIGHT - 50
player_speed = 5

# Bullets
bullets = []
bullet_speed = 7

# Alien bullets
alien_bullets = []
alien_bullet_speed = 3

# Bases
bases = []
for i in range(4):
    base_x = 150 + i * 150
    base_y = HEIGHT - 150
    # Create base blocks (simple rectangular base)
    for row in range(3):
        for col in range(8):
            if not (row == 2 and 2 <= col <= 5):  # Create opening at bottom
                bases.append([base_x + col * 8, base_y + row * 8])

# Invaders
invaders = []
for row in range(5):
    for col in range(10):
        invaders.append([col * 60 + 100, row * 40 + 50])

invader_speed = 1
invader_direction = 1

# Game states
game_state = "menu"  # "menu", "playing", "game_over"
difficulty = 1

# UFO bonus ship
ufo = None
ufo_spawn_timer = 0

# Weapon system
weapon_drops = []
current_weapon = "normal"
weapon_timer = 0

# Score
score = 0

game_over = False
font = pygame.font.Font(None, 74)
small_font = pygame.font.Font(None, 36)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if game_state == "menu":
                if pygame.K_1 <= event.key <= pygame.K_5:
                    difficulty = event.key - pygame.K_0
                    game_state = "playing"
            elif game_state == "game_over" and event.key == pygame.K_q:
                running = False
            elif game_state == "playing" and event.key == pygame.K_SPACE:
                if current_weapon == "normal":
                    bullets.append([player_x + 15, player_y])
                elif current_weapon == "split":
                    bullets.append([player_x + 15, player_y])
                    bullets.append([player_x + 5, player_y])
                    bullets.append([player_x + 25, player_y])
                elif current_weapon == "laser":
                    bullets.append([player_x + 15, player_y])
                elif current_weapon == "homing":
                    bullets.append([player_x + 15, player_y])

    if game_state == "playing":
        # Player movement
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and player_x > 0:
            player_x -= player_speed
        if keys[pygame.K_RIGHT] and player_x < WIDTH - 30:
            player_x += player_speed

        # Move bullets
        for bullet in bullets[:]:
            if current_weapon == "homing" and invaders:
                # Find closest invader
                closest = min(invaders, key=lambda inv: abs(bullet[0] - inv[0]))
                if bullet[0] < closest[0]:
                    bullet[0] += 1
                elif bullet[0] > closest[0]:
                    bullet[0] -= 1
            bullet[1] -= bullet_speed
            if bullet[1] < 0:
                bullets.remove(bullet)

        # Move weapon drops
        for drop in weapon_drops[:]:
            drop[1] += 2
            if drop[1] > HEIGHT:
                weapon_drops.remove(drop)

        # Weapon timer countdown
        if weapon_timer > 0:
            weapon_timer -= 1
            if weapon_timer == 0:
                current_weapon = "normal"

        # Move alien bullets
        alien_bullets = [[x, y + alien_bullet_speed] for x, y in alien_bullets if y < HEIGHT]

        # Aliens shoot based on difficulty and remaining count
        base_shoot_chance = 200 - (difficulty * 30)
        aggression_multiplier = max(1, 50 - len(invaders)) * 2  # More aggressive with fewer aliens
        shoot_chance = max(1, base_shoot_chance - aggression_multiplier)
        if random.randint(1, shoot_chance) == 1 and invaders:
            shooter = random.choice(invaders)
            alien_bullets.append([shooter[0] + 15, shooter[1] + 20])

        # UFO spawning and movement
        ufo_spawn_timer += 1
        if ufo_spawn_timer > 300 and not ufo:  # Spawn every 5 seconds
            ufo = [-50, 30]  # Start off-screen left
            ufo_spawn_timer = 0
        
        if ufo:
            ufo[0] += 2  # Move right
            if ufo[0] > WIDTH:  # Remove when off-screen
                ufo = None

        # Move invaders (speed based on difficulty)
        base_speed = invader_speed * (0.5 + difficulty * 0.2)  # Difficulty multiplier
        current_speed = base_speed + (50 - len(invaders)) * 0.05 * difficulty
        move_down = False
        for invader in invaders:
            invader[0] += current_speed * invader_direction
            if invader[0] <= 0 or invader[0] >= WIDTH - 30:
                move_down = True
        
        if move_down:
            invader_direction *= -1
            for invader in invaders:
                invader[1] += 20

        # Collision detection - bullets hit invaders
        for bullet in bullets[:]:
            hit = False
            for invader in invaders[:]:
                if (bullet[0] < invader[0] + 30 and bullet[0] + 5 > invader[0] and
                    bullet[1] < invader[1] + 20 and bullet[1] + 10 > invader[1]):
                    if current_weapon == "laser":
                        # Laser pierces through
                        invaders.remove(invader)
                        score += 10
                    else:
                        bullets.remove(bullet)
                        invaders.remove(invader)
                        score += 10
                        hit = True
                        break
            if hit:
                break

        # Collision detection - bullets hit UFO
        if ufo:
            for bullet in bullets[:]:
                if (bullet[0] < ufo[0] + 40 and bullet[0] + 5 > ufo[0] and
                    bullet[1] < ufo[1] + 15 and bullet[1] + 10 > ufo[1]):
                    bullets.remove(bullet)
                    score += 100
                    # Drop random weapon
                    weapons = ["split", "laser", "homing"]
                    weapon_drops.append([ufo[0] + 20, ufo[1], random.choice(weapons)])
                    ufo = None
                    break

        # Collision detection - player collects weapon drops
        for drop in weapon_drops[:]:
            if (drop[0] < player_x + 30 and drop[0] + 20 > player_x and
                drop[1] < player_y + 20 and drop[1] + 10 > player_y):
                current_weapon = drop[2]
                weapon_timer = 1800  # 30 seconds
                weapon_drops.remove(drop)

        # Collision detection - bullets hit bases
        for bullet in bullets[:]:
            for base in bases[:]:
                if (bullet[0] < base[0] + 8 and bullet[0] + 5 > base[0] and
                    bullet[1] < base[1] + 8 and bullet[1] + 10 > base[1]):
                    bullets.remove(bullet)
                    bases.remove(base)
                    break

        # Collision detection - alien bullets hit bases
        for alien_bullet in alien_bullets[:]:
            for base in bases[:]:
                if (alien_bullet[0] < base[0] + 8 and alien_bullet[0] + 5 > base[0] and
                    alien_bullet[1] < base[1] + 8 and alien_bullet[1] + 10 > base[1]):
                    alien_bullets.remove(alien_bullet)
                    bases.remove(base)
                    break

        # Collision detection - alien bullets hit player
        for alien_bullet in alien_bullets[:]:
            if (alien_bullet[0] < player_x + 30 and alien_bullet[0] + 5 > player_x and
                alien_bullet[1] < player_y + 20 and alien_bullet[1] + 10 > player_y):
                game_state = "game_over"

        # Collision detection - aliens hit player
        for invader in invaders:
            if (invader[0] < player_x + 30 and invader[0] + 30 > player_x and
                invader[1] < player_y + 20 and invader[1] + 20 > player_y):
                game_state = "game_over"

        # Check win condition
        if not invaders:
            game_state = "game_over"

    # Draw everything
    screen.fill(BLACK)
    
    if game_state == "menu":
        title_text = font.render("SPACE INVADERS", True, WHITE)
        diff_text = small_font.render("Select Difficulty (1-5):", True, WHITE)
        easy_text = small_font.render("1 = Easy", True, GREEN)
        hard_text = small_font.render("5 = Hard", True, RED)
        
        screen.blit(title_text, (WIDTH//2 - title_text.get_width()//2, HEIGHT//2 - 100))
        screen.blit(diff_text, (WIDTH//2 - diff_text.get_width()//2, HEIGHT//2 - 30))
        screen.blit(easy_text, (WIDTH//2 - easy_text.get_width()//2, HEIGHT//2 + 10))
        screen.blit(hard_text, (WIDTH//2 - hard_text.get_width()//2, HEIGHT//2 + 50))
        
    elif game_state == "game_over":
        if invaders:
            game_text = font.render("GAME OVER!", True, RED)
        else:
            game_text = font.render("YOU WIN!", True, WHITE)
        quit_text = font.render("Press Q to quit", True, WHITE)
        screen.blit(game_text, (WIDTH//2 - game_text.get_width()//2, HEIGHT//2 - 50))
        screen.blit(quit_text, (WIDTH//2 - quit_text.get_width()//2, HEIGHT//2 + 20))
        
    else:  # playing
        # Draw score and weapon info
        score_text = small_font.render(f"Score: {score}", True, WHITE)
        screen.blit(score_text, (10, 10))
        
        if current_weapon != "normal":
            weapon_text = small_font.render(f"Weapon: {current_weapon.upper()} ({weapon_timer//60}s)", True, (0, 255, 0))
            screen.blit(weapon_text, (10, 40))
        
        screen.blit(player_img, (player_x, player_y))
        
        for bullet in bullets:
            color = (0, 255, 255) if current_weapon == "laser" else WHITE
            pygame.draw.rect(screen, color, (bullet[0], bullet[1], 5, 10))
        
        for alien_bullet in alien_bullets:
            pygame.draw.rect(screen, RED, (alien_bullet[0], alien_bullet[1], 5, 10))
        
        for base in bases:
            pygame.draw.rect(screen, WHITE, (base[0], base[1], 8, 8))
        
        for invader in invaders:
            screen.blit(invader_img, (invader[0], invader[1]))
        
        # Draw weapon drops
        for drop in weapon_drops:
            color = (255, 255, 0) if drop[2] == "split" else (0, 255, 255) if drop[2] == "laser" else (255, 0, 255)
            pygame.draw.rect(screen, color, (drop[0], drop[1], 20, 10))
        
        # Draw UFO
        if ufo:
            screen.blit(ufo_img, (ufo[0], ufo[1]))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
