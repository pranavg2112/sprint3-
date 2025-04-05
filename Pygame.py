import math
import random
import sys

"To try the game, install PYGAME module in the terminal you are running. Command to install: pip install pygame"

import pygame

pygame.init()

WIDTH, HEIGHT = 850, 650
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("mQIX Game")

WHITE  = (255, 255, 255)
BLACK  = (0,   0,   0)
GRAY   = (200, 200, 200)
BLUE   = (0,   0, 255)
RED    = (255, 0,   0)
GREEN  = (0, 255,   0)
YELLOW = (255, 255, 0)
PURPLE = (150, 0,  150)

FPS = 60
clock = pygame.time.Clock()

UI_HEIGHT = 85

margin = 120

game_area = pygame.Rect(
    margin,
    UI_HEIGHT,
    WIDTH - margin,
    HEIGHT - UI_HEIGHT
)

player_size = 10
player_speed = 5
player_lives = 3

player_x = game_area.left
player_y = game_area.top

incursion_mode = False
incursion_path = []

qix_size = 10
qix_speed = 4
qix_x = random.randint(game_area.left, game_area.right)
qix_y = random.randint(game_area.top, game_area.bottom)
qix_vx = random.choice([-qix_speed, qix_speed])
qix_vy = random.choice([-qix_speed, qix_speed])
change_direction_counter = 0

sparx_size = 10
sparx_speed = 3
sparx_x = game_area.right
sparx_y = game_area.top
sparx_direction = "down"

level = 1

font = pygame.font.SysFont(None, 36)

def draw_text(text, x, y, color=WHITE, bg_color=BLACK):
    img = font.render(text, True, color)
    text_rect = img.get_rect(topleft=(x, y))
    pygame.draw.rect(screen, bg_color, text_rect)
    screen.blit(img, text_rect)

def reset_incursion():
    global incursion_mode, incursion_path
    incursion_mode = False
    incursion_path = []

def is_on_border(x, y):
    return (
        x <= game_area.left or
        x >= game_area.right or
        y <= game_area.top or
        y >= game_area.bottom
    )

def compute_polygon_area(points):
    if len(points) < 3:
        return 0
    area = 0
    n = len(points)
    for i in range(n):
        x1, y1 = points[i]
        x2, y2 = points[(i + 1) % n]
        area += (x1 * y2) - (y1 * x2)
    return abs(area) / 2

claimed_polygons = []
total_claimed_area = 0
total_playable_area = game_area.width * game_area.height

running = True
while running:
    clock.tick(FPS)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    dx = 0
    dy = 0
    if keys[pygame.K_LEFT]:
        dx = -player_speed
    if keys[pygame.K_RIGHT]:
        dx = player_speed
    if keys[pygame.K_UP]:
        dy = -player_speed
    if keys[pygame.K_DOWN]:
        dy = player_speed

    player_x += dx
    player_y += dy

    player_x = max(game_area.left, min(player_x, game_area.right))
    player_y = max(game_area.top, min(player_y, game_area.bottom))

    if keys[pygame.K_SPACE] and is_on_border(player_x, player_y):
        if not incursion_mode:
            incursion_mode = True
            incursion_path = [(player_x, player_y)]
    
    if incursion_mode:
        incursion_path.append((player_x, player_y))
        if is_on_border(player_x, player_y) and len(incursion_path) > 10:
            area = compute_polygon_area(incursion_path)
            claimed_polygons.append(list(incursion_path))
            total_claimed_area += area
            reset_incursion()

    qix_x += qix_vx
    qix_y += qix_vy

    if qix_x <= game_area.left or qix_x >= game_area.right:
        qix_vx = -qix_vx
    if qix_y <= game_area.top or qix_y >= game_area.bottom:
        qix_vy = -qix_vy

    change_direction_counter += 1
    if change_direction_counter >= 30:
        qix_vx = random.choice([-qix_speed, qix_speed])
        qix_vy = random.choice([-qix_speed, qix_speed])
        change_direction_counter = 0

    if incursion_mode:
        for point in incursion_path:
            if abs(qix_x - point[0]) < qix_size and abs(qix_y - point[1]) < qix_size:
                player_lives -= 1
                reset_incursion()
                break

    if sparx_direction == "right":
        sparx_x += sparx_speed
        if sparx_x >= game_area.right:
            sparx_direction = "down"
    elif sparx_direction == "down":
        sparx_y += sparx_speed
        if sparx_y >= game_area.bottom:
            sparx_direction = "left"
    elif sparx_direction == "left":
        sparx_x -= sparx_speed
        if sparx_x <= game_area.left:
            sparx_direction = "up"
    elif sparx_direction == "up":
        sparx_y -= sparx_speed
        if sparx_y <= game_area.top:
            sparx_direction = "right"

    if is_on_border(player_x, player_y):
        if abs(sparx_x - player_x) < sparx_size and abs(sparx_y - player_y) < sparx_size:
            player_lives -= 1

    claimed_area_percentage = (total_claimed_area / total_playable_area) * 100

    if claimed_area_percentage >= 50:
        level += 1
        claimed_polygons = []
        total_claimed_area = 0

    if player_lives <= 0:
        screen.fill(BLACK)
        draw_text("Game Over!", WIDTH // 2 - 80, HEIGHT // 2 - 20, RED)
        pygame.display.flip()
        pygame.time.delay(3000)
        running = False
        continue

    screen.fill(BLACK)

    for poly in claimed_polygons:
        pygame.draw.polygon(screen, PURPLE, poly)

    pygame.draw.rect(screen, GRAY, game_area, 2)

    if incursion_mode and len(incursion_path) > 1:
        pygame.draw.lines(screen, YELLOW, False, incursion_path, 4)

    pygame.draw.circle(screen, BLUE, (int(player_x), int(player_y)), player_size)
    pygame.draw.circle(screen, RED, (int(qix_x), int(qix_y)), qix_size)
    pygame.draw.circle(screen, GREEN, (int(sparx_x), int(sparx_y)), sparx_size)

    draw_text(f"Lives: {player_lives}", 20, 20)
    draw_text(f"Claimed Area: {claimed_area_percentage:.1f}%", 20, 50)
    draw_text(f"Level: {level}", 20, 80)

    pygame.display.flip()

pygame.quit()
sys.exit()
