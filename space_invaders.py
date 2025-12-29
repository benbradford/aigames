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
exp_img = pygame.image.load("exp.png")
exp_img = pygame.transform.scale(exp_img, (30, 30))

# Special alien images
kamikaze_img = pygame.image.load("kamikaze.png")
kamikaze_img = pygame.transform.scale(kamikaze_img, (30, 20))
shield_img = pygame.image.load("shield.png")
shield_img = pygame.transform.scale(shield_img, (30, 20))
zigzag_img = pygame.image.load("zigzag.png")
zigzag_img = pygame.transform.scale(zigzag_img, (30, 20))
sniper_img = pygame.image.load("sniper.png")
sniper_img = pygame.transform.scale(sniper_img, (30, 20))
spawner_img = pygame.image.load("spawner.png")
spawner_img = pygame.transform.scale(spawner_img, (30, 20))
mini_img = pygame.image.load("mini.png")
mini_img = pygame.transform.scale(mini_img, (15, 10))

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

# Wave system
wave_spawn_timer = 0
base_regen_timer = 0

# Special aliens
special_aliens = []
special_spawn_timer = 0
mini_aliens = []

# Explosions
explosions = []

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
                elif current_weapon == "super":
                    bullets.append([player_x + 10, player_y])  # Centered for bigger bullet

    if game_state == "playing":
        # Player movement
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and player_x > 0:
            player_x -= player_speed
        if keys[pygame.K_RIGHT] and player_x < WIDTH - 30:
            player_x += player_speed

        # Move bullets
        for bullet in bullets[:]:
            bullet[1] -= bullet_speed
            if bullet[1] < 0:
                bullets.remove(bullet)

        # Move weapon drops
        for drop in weapon_drops[:]:
            drop[1] += 4  # Doubled from 2 to 4
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
        aggression_multiplier = max(1, (50 - len(invaders)) * 0.5)  # Reduced multiplier
        shoot_chance = max(20, base_shoot_chance - aggression_multiplier)  # Minimum of 20
        if random.randint(1, int(shoot_chance)) == 1 and invaders:
            shooter = random.choice(invaders)
            alien_bullets.append([shooter[0] + 15, shooter[1] + 20])

        # Spawn special aliens
        special_spawn_timer += 1
        if special_spawn_timer > 900:  # Every 15 seconds
            alien_types = ["kamikaze", "shield", "zigzag", "sniper", "spawner"]
            alien_type = random.choice(alien_types)
            if alien_type == "kamikaze":
                special_aliens.append([random.randint(50, WIDTH-50), -30, alien_type, 3])  # x, y, type, speed
            elif alien_type == "shield":
                special_aliens.append([random.randint(50, WIDTH-50), 100, alien_type, 3])  # 3 hits to kill
            elif alien_type == "zigzag":
                special_aliens.append([50, -30, alien_type, 1])  # direction: 1=right, -1=left
            elif alien_type == "sniper":
                side = random.choice([0, WIDTH-30])
                special_aliens.append([side, 80, alien_type, 0])  # shoot timer
            elif alien_type == "spawner":
                special_aliens.append([random.randint(100, WIDTH-100), 60, alien_type, 0])  # spawn count
            special_spawn_timer = 0
        # UFO spawning and movement (more frequent on easier difficulties)
        ufo_spawn_timer += 1
        ufo_spawn_frequency = 600 - (difficulty - 1) * 100  # Easy=200, Hard=600
        if ufo_spawn_timer > ufo_spawn_frequency and not ufo:
            ufo = [-50, 30]  # Start off-screen left
            ufo_spawn_timer = 0
        
        if ufo:
            ufo[0] += 2  # Move right
            if ufo[0] > WIDTH:  # Remove when off-screen
                ufo = None

        # Move special aliens
        for alien in special_aliens[:]:
            if alien[2] == "kamikaze":
                alien[1] += alien[3]  # Move down fast
                if alien[1] > HEIGHT:
                    alien[1] = -30  # Respawn at top
            elif alien[2] == "shield":
                alien[1] += 1  # Move down slowly
                if alien[1] > HEIGHT:
                    alien[1] = -30  # Respawn at top
                # Shoot frequently
                if random.randint(1, 30) == 1:
                    alien_bullets.append([alien[0] + 15, alien[1] + 20])
            elif alien[2] == "zigzag":
                alien[1] += 2  # Move down
                alien[0] += alien[3] * 3  # Move sideways
                if alien[0] <= 0 or alien[0] >= WIDTH - 30:
                    alien[3] *= -1  # Change direction
                if alien[1] > HEIGHT:
                    alien[1] = -30  # Respawn at top
                # Shoot randomly
                if random.randint(1, 60) == 1:
                    alien_bullets.append([alien[0] + 15, alien[1] + 20])
            elif alien[2] == "sniper":
                alien[3] += 1  # Shoot timer
                if alien[3] > 120:  # Shoot every 2 seconds
                    # Aim at player
                    alien_bullets.append([alien[0] + 15, alien[1] + 20])
                    alien[3] = 0
                # Move down slowly
                alien[1] += 0.5
                if alien[1] > HEIGHT:
                    alien[1] = -30  # Respawn at top
            elif alien[2] == "spawner":
                alien[3] += 1  # Spawn timer
                if alien[3] > 180 and len(mini_aliens) < 10:  # Spawn every 3 seconds
                    mini_aliens.append([alien[0], alien[1] + 20])
                    alien[3] = 0
                if alien[1] > HEIGHT:
                    alien[1] = -30  # Respawn at top
                # Remove after spawning 4 mini-aliens
                if len([m for m in mini_aliens if abs(m[0] - alien[0]) < 50]) >= 4:
                    special_aliens.remove(alien)

        # Move explosions
        for explosion in explosions[:]:
            explosion[2] -= 1  # Decrease timer
            if explosion[2] <= 0:
                explosions.remove(explosion)

        # Move mini aliens
        for mini in mini_aliens[:]:
            mini[1] += 3  # Move down faster (increased from 2 to 3)
            if mini[1] > HEIGHT:
                mini_aliens.remove(mini)

        # Spawn new invader waves (every 20 seconds)
        wave_spawn_timer += 1
        if wave_spawn_timer > 1200:  # Every 20 seconds
            for col in range(10):
                invaders.append([col * 60 + 100, 50])  # Add new row at top
            wave_spawn_timer = 0

        # Regenerate bases over time
        base_regen_timer += 1
        if base_regen_timer > 300:  # Every 5 seconds
            # Add some base blocks back
            for i in range(4):
                base_x = 150 + i * 150
                base_y = HEIGHT - 150
                # Count existing blocks for this base
                existing_count = len([b for b in bases if base_x <= b[0] <= base_x + 64 and base_y <= b[1] <= base_y + 24])
                if existing_count < 15:  # If base is damaged (originally had ~20 blocks)
                    # Add a few blocks back
                    for row in range(3):
                        for col in range(8):
                            if not (row == 2 and 2 <= col <= 5):  # Skip opening
                                block_x = base_x + col * 8
                                block_y = base_y + row * 8
                                # Check if block already exists
                                if not any(abs(b[0] - block_x) < 4 and abs(b[1] - block_y) < 4 for b in bases):
                                    bases.append([block_x, block_y])
                                    break  # Only add one block per base per cycle
                        else:
                            continue
                        break
            base_regen_timer = 0

        # Move invaders (speed based on difficulty)
        base_speed = invader_speed * (0.5 + difficulty * 0.2)  # Difficulty multiplier
        current_speed = base_speed + (50 - len(invaders)) * 0.05 * difficulty
        move_down = False
        move_up = False
        for invader in invaders:
            invader[0] += current_speed * invader_direction
            if invader[0] <= 0 or invader[0] >= WIDTH - 30:
                move_down = True
        
        # Check if invaders hit bottom or top
        bottom_hit = any(invader[1] >= HEIGHT - 100 for invader in invaders)
        top_hit = any(invader[1] <= 50 for invader in invaders)
        
        if move_down:
            invader_direction *= -1
            if bottom_hit:
                # Reverse vertical direction - go up
                for invader in invaders:
                    invader[1] -= 10
            elif top_hit:
                # Reverse vertical direction - go down  
                for invader in invaders:
                    invader[1] += 10
            else:
                # Normal downward movement
                for invader in invaders:
                    invader[1] += 10

        # Collision detection - bullets hit invaders
        for bullet in bullets[:]:
            hit = False
            bullet_width = 10 if current_weapon == "super" else 5
            for invader in invaders[:]:
                if (bullet[0] < invader[0] + 30 and bullet[0] + bullet_width > invader[0] and
                    bullet[1] < invader[1] + 20 and bullet[1] + 10 > invader[1]):
                    explosions.append([invader[0], invader[1], 30])  # x, y, timer
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

        # Collision detection - bullets hit special aliens
        for bullet in bullets[:]:
            hit = False
            for alien in special_aliens[:]:
                if (bullet[0] < alien[0] + 30 and bullet[0] + 5 > alien[0] and
                    bullet[1] < alien[1] + 20 and bullet[1] + 10 > alien[1]):
                    explosions.append([alien[0], alien[1], 30])  # Add explosion
                    if alien[2] == "shield":
                        alien[3] -= 1  # Reduce health
                        if alien[3] <= 0:
                            special_aliens.remove(alien)
                            score += 50
                        else:
                            score += 10
                    else:
                        special_aliens.remove(alien)
                        score += 30
                    if current_weapon != "laser":
                        bullets.remove(bullet)
                        hit = True
                        break
            if hit:
                break

        # Collision detection - bullets hit mini aliens
        for bullet in bullets[:]:
            for mini in mini_aliens[:]:
                if (bullet[0] < mini[0] + 15 and bullet[0] + 5 > mini[0] and
                    bullet[1] < mini[1] + 10 and bullet[1] + 10 > mini[1]):
                    explosions.append([mini[0], mini[1], 20])  # Smaller explosion
                    bullets.remove(bullet)
                    mini_aliens.remove(mini)
                    score += 5
                    break
        # Collision detection - bullets hit UFO
        if ufo:
            for bullet in bullets[:]:
                if (bullet[0] < ufo[0] + 40 and bullet[0] + 5 > ufo[0] and
                    bullet[1] < ufo[1] + 15 and bullet[1] + 10 > ufo[1]):
                    explosions.append([ufo[0], ufo[1], 40])  # Bigger explosion for UFO
                    bullets.remove(bullet)
                    score += 100
                    # Drop random weapon
                    weapons = ["split", "laser", "super"]
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

        # Collision detection - special aliens hit player
        for alien in special_aliens:
            if (alien[0] < player_x + 30 and alien[0] + 30 > player_x and
                alien[1] < player_y + 20 and alien[1] + 20 > player_y):
                game_state = "game_over"

        # Collision detection - mini aliens hit player  
        for mini in mini_aliens:
            if (mini[0] < player_x + 30 and mini[0] + 15 > player_x and
                mini[1] < player_y + 20 and mini[1] + 10 > player_y):
                game_state = "game_over"

        # Check win condition
        if not invaders and not special_aliens:
            game_state = "game_over"

    # Draw everything
    screen.fill(BLACK)
    
    if game_state == "menu":
        title_text = font.render("SPACE INVADERS", True, WHITE)
        diff_text = small_font.render("Select Difficulty (1-5):", True, WHITE)
        diff1_text = small_font.render("1 = Beginner", True, GREEN)
        diff2_text = small_font.render("2 = Rookie", True, (150, 255, 150))
        diff3_text = small_font.render("3 = Average", True, (255, 255, 150))
        diff4_text = small_font.render("4 = Hard", True, (255, 150, 150))
        diff5_text = small_font.render("5 = Nightmare", True, RED)
        
        screen.blit(title_text, (WIDTH//2 - title_text.get_width()//2, HEIGHT//2 - 140))
        screen.blit(diff_text, (WIDTH//2 - diff_text.get_width()//2, HEIGHT//2 - 60))
        screen.blit(diff1_text, (WIDTH//2 - diff1_text.get_width()//2, HEIGHT//2 - 20))
        screen.blit(diff2_text, (WIDTH//2 - diff2_text.get_width()//2, HEIGHT//2 + 10))
        screen.blit(diff3_text, (WIDTH//2 - diff3_text.get_width()//2, HEIGHT//2 + 40))
        screen.blit(diff4_text, (WIDTH//2 - diff4_text.get_width()//2, HEIGHT//2 + 70))
        screen.blit(diff5_text, (WIDTH//2 - diff5_text.get_width()//2, HEIGHT//2 + 100))
        
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
            if current_weapon == "super":
                pygame.draw.rect(screen, (255, 255, 0), (bullet[0], bullet[1], 10, 20))  # Bigger yellow bullet
            else:
                color = (0, 255, 255) if current_weapon == "laser" else WHITE
                pygame.draw.rect(screen, color, (bullet[0], bullet[1], 5, 10))
        
        for alien_bullet in alien_bullets:
            pygame.draw.rect(screen, RED, (alien_bullet[0], alien_bullet[1], 5, 10))
        
        for base in bases:
            pygame.draw.rect(screen, WHITE, (base[0], base[1], 8, 8))
        
        for invader in invaders:
            screen.blit(invader_img, (invader[0], invader[1]))
        
        # Draw special aliens
        for alien in special_aliens:
            if alien[2] == "kamikaze":
                screen.blit(kamikaze_img, (alien[0], alien[1]))
            elif alien[2] == "shield":
                screen.blit(shield_img, (alien[0], alien[1]))
            elif alien[2] == "zigzag":
                screen.blit(zigzag_img, (alien[0], alien[1]))
            elif alien[2] == "sniper":
                screen.blit(sniper_img, (alien[0], alien[1]))
            elif alien[2] == "spawner":
                screen.blit(spawner_img, (alien[0], alien[1]))
        
        # Draw mini aliens
        for mini in mini_aliens:
            screen.blit(mini_img, (mini[0], mini[1]))
        
        # Draw explosions
        for explosion in explosions:
            screen.blit(exp_img, (explosion[0], explosion[1]))
        
        # Draw weapon drops
        for drop in weapon_drops:
            color = (255, 255, 0) if drop[2] == "split" else (0, 255, 255) if drop[2] == "laser" else (255, 100, 0)
            pygame.draw.rect(screen, color, (drop[0], drop[1], 20, 10))
        
        # Draw UFO
        if ufo:
            screen.blit(ufo_img, (ufo[0], ufo[1]))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
