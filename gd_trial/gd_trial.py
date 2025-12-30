import pygame
import sys

pygame.init()

WIDTH, HEIGHT = 900, 500
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("GD Platformer")

clock = pygame.time.Clock()

# ---------------- COLORS ----------------
WHITE = (255, 255, 255)
BLUE = (50, 100, 255)
RED = (200, 50, 50)
YELLOW = (255, 220, 50)
CYAN = (80, 200, 255)
GRAY = (120, 120, 120)
DARK_GRAY = (90, 90, 90)

# ---------------- PLAYER ----------------
PLAYER_SIZE = 40
BLOCK_SIZE = 40

MOVE_SPEED = 5
JUMP_FORCE = 12
ORB_BOUNCE_FORCE = 12
PAD_BOUNCE_FORCE = 14
GRAVITY = 0.6

gravity_dir = 1
rotation_angle = 0
ROTATION_SPEED = 6

player_surface = pygame.Surface((PLAYER_SIZE, PLAYER_SIZE), pygame.SRCALPHA)
player_surface.fill(BLUE)

# ---------------- ROOMS ----------------
current_room = "testing"

GROUND_Y = 400
CEILING_Y = 80
BLOCK_HEIGHT = 40

LEFT_WALL_X = 0
START_POS = pygame.Vector2(LEFT_WALL_X + BLOCK_SIZE + 10, 300)

player_pos = START_POS.copy()
player_vel = pygame.Vector2(0, 0)

# ---------------- TESTING ROOM GEOMETRY ----------------
PIT_LEFT_X = 300
PIT_RIGHT_X = 540
PIT_WALL_WIDTH = 40
PIT_FLOOR_Y = GROUND_Y - BLOCK_HEIGHT

testing_blocks = [
    pygame.Rect(LEFT_WALL_X, 0, BLOCK_HEIGHT, HEIGHT),
    pygame.Rect(0, GROUND_Y, WIDTH, BLOCK_HEIGHT),
    pygame.Rect(0, CEILING_Y, WIDTH, BLOCK_HEIGHT),
    pygame.Rect(PIT_LEFT_X, GROUND_Y - 160, PIT_WALL_WIDTH, 160),
    pygame.Rect(PIT_RIGHT_X - PIT_WALL_WIDTH, GROUND_Y - 160, PIT_WALL_WIDTH, 160),
    pygame.Rect(
        PIT_LEFT_X + PIT_WALL_WIDTH,
        PIT_FLOOR_Y,
        (PIT_RIGHT_X - PIT_LEFT_X) - PIT_WALL_WIDTH * 2,
        BLOCK_HEIGHT
    ),
]

# ---------------- SPIKES ----------------
SPIKE_SIZE = 30
spikes = []
spike_hitboxes = []

for x in range(PIT_LEFT_X + PIT_WALL_WIDTH, PIT_RIGHT_X - PIT_WALL_WIDTH, SPIKE_SIZE):
    y = PIT_FLOOR_Y
    spikes.append([(x, y), (x + SPIKE_SIZE // 2, y - SPIKE_SIZE), (x + SPIKE_SIZE, y)])
    spike_hitboxes.append(pygame.Rect(x + 9, y - 18, 12, 18))

# ---------------- ORBS ----------------
ORB_RADIUS = 12

entry_orb_pos = pygame.Vector2(PIT_LEFT_X - 40, GROUND_Y - 60)
pit_orb_pos = pygame.Vector2((PIT_LEFT_X + PIT_RIGHT_X) // 2, PIT_FLOOR_Y - 50)
blue_orb_pos = pygame.Vector2(120, GROUND_Y - 120)

def orb_rect(pos):
    return pygame.Rect(pos.x - ORB_RADIUS, pos.y - ORB_RADIUS,
                       ORB_RADIUS * 2, ORB_RADIUS * 2)

entry_orb_rect = orb_rect(entry_orb_pos)
pit_orb_rect = orb_rect(pit_orb_pos)
blue_orb_rect = orb_rect(blue_orb_pos)

entry_orb_used = pit_orb_used = blue_orb_used = False

# ---------------- PADS ----------------
PAD_WIDTH, PAD_HEIGHT = 40, 12
yellow_pad = pygame.Rect(200, GROUND_Y - PAD_HEIGHT, PAD_WIDTH, PAD_HEIGHT)
blue_pad = pygame.Rect(650, GROUND_Y - PAD_HEIGHT, PAD_WIDTH, PAD_HEIGHT)

yellow_pad_used = blue_pad_used = False

# ---------------- TEXT ----------------
font = pygame.font.SysFont(None, 72)
testing_text = font.render("TESTING", True, DARK_GRAY)
main_text = font.render("MAIN ROOM", True, DARK_GRAY)

on_ground = False

# ---------------- MAIN LOOP ----------------
while True:
    clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    keys = pygame.key.get_pressed()
    holding_jump = keys[pygame.K_SPACE]

    # Horizontal movement
    player_vel.x = (keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]) * MOVE_SPEED

    # Jump
    if holding_jump and on_ground:
        player_vel.y = -JUMP_FORCE * gravity_dir
        on_ground = False

    # Gravity
    player_vel.y += GRAVITY * gravity_dir

    # Select room blocks
    blocks = testing_blocks if current_room == "testing" else [
        pygame.Rect(0, GROUND_Y, WIDTH, BLOCK_HEIGHT),
        pygame.Rect(0, CEILING_Y, WIDTH, BLOCK_HEIGHT),
    ]

    # ---------- X movement ----------
    player_pos.x += player_vel.x
    player_rect = pygame.Rect(player_pos.x, player_pos.y, PLAYER_SIZE, PLAYER_SIZE)

    for block in blocks:
        if player_rect.colliderect(block):
            if player_vel.x > 0:
                player_pos.x = block.left - PLAYER_SIZE
            elif player_vel.x < 0:
                player_pos.x = block.right

    # ---------- Y movement ----------
    player_pos.y += player_vel.y
    player_rect = pygame.Rect(player_pos.x, player_pos.y, PLAYER_SIZE, PLAYER_SIZE)

    on_ground = False
    for block in blocks:
        if not player_rect.colliderect(block):
            continue

        if gravity_dir == 1:
            if player_vel.y > 0:
                player_pos.y = block.top - PLAYER_SIZE
                player_vel.y = 0
                on_ground = True
                rotation_angle = 0
            elif player_vel.y < 0:
                player_pos.y = block.bottom
                player_vel.y = 0
        else:
            if player_vel.y < 0:
                player_pos.y = block.bottom
                player_vel.y = 0
                on_ground = True
                rotation_angle = 0
            elif player_vel.y > 0:
                player_pos.y = block.top - PLAYER_SIZE
                player_vel.y = 0

    # Rotation
    if not on_ground:
        if player_vel.x > 0:
            rotation_angle -= ROTATION_SPEED
        elif player_vel.x < 0:
            rotation_angle += ROTATION_SPEED
        rotation_angle %= 360

    # ---------- ORBS & PADS (TESTING ROOM ONLY) ----------
    if current_room == "testing":
        if holding_jump and player_rect.colliderect(entry_orb_rect) and not entry_orb_used:
            player_vel.y = -ORB_BOUNCE_FORCE * gravity_dir
            entry_orb_used = True

        if holding_jump and player_rect.colliderect(pit_orb_rect) and not pit_orb_used:
            player_vel.y = -ORB_BOUNCE_FORCE * gravity_dir
            pit_orb_used = True

        if holding_jump and player_rect.colliderect(blue_orb_rect) and not blue_orb_used:
            player_vel.y = -ORB_BOUNCE_FORCE * gravity_dir
            gravity_dir *= -1
            blue_orb_used = True

        if player_rect.colliderect(yellow_pad) and not yellow_pad_used:
            player_vel.y = -PAD_BOUNCE_FORCE * gravity_dir
            yellow_pad_used = True

        if player_rect.colliderect(blue_pad) and not blue_pad_used:
            player_vel.y = -PAD_BOUNCE_FORCE * gravity_dir
            gravity_dir *= -1
            blue_pad_used = True

        entry_orb_used &= player_rect.colliderect(entry_orb_rect)
        pit_orb_used &= player_rect.colliderect(pit_orb_rect)
        blue_orb_used &= player_rect.colliderect(blue_orb_rect)
        yellow_pad_used &= player_rect.colliderect(yellow_pad)
        blue_pad_used &= player_rect.colliderect(blue_pad)

        for hitbox in spike_hitboxes:
            if player_rect.colliderect(hitbox):
                pygame.time.delay(600)
                player_pos = START_POS.copy()
                player_vel.update(0, 0)
                gravity_dir = 1
                rotation_angle = 0

    # ---------- ROOM TRANSITION ----------
    if current_room == "testing" and player_pos.x > WIDTH:
        current_room = "main"
        player_pos.x = WIDTH - PLAYER_SIZE - 10
        player_vel.x = 0

    # ---------- DRAW ----------
    screen.fill(WHITE)

    for block in blocks:
        pygame.draw.rect(screen, GRAY, block)

    if current_room == "testing":
        for spike in spikes:
            pygame.draw.polygon(screen, RED, spike)

        pygame.draw.rect(screen, YELLOW, yellow_pad)
        pygame.draw.rect(screen, CYAN, blue_pad)
        pygame.draw.circle(screen, YELLOW, entry_orb_pos, ORB_RADIUS)
        pygame.draw.circle(screen, YELLOW, pit_orb_pos, ORB_RADIUS)
        pygame.draw.circle(screen, CYAN, blue_orb_pos, ORB_RADIUS)

        screen.blit(testing_text, (WIDTH // 2 - 120, 30))
    else:
        screen.blit(main_text, (WIDTH // 2 - 150, 30))

    rotated = pygame.transform.rotate(player_surface, rotation_angle)
    screen.blit(rotated, rotated.get_rect(center=player_rect.center))

    pygame.display.flip()
