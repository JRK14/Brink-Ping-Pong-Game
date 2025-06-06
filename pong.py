import pygame
import sys

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 400
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PADDLE_WIDTH, PADDLE_HEIGHT = 10, 60
BALL_SIZE = 10
PADDLE_SPEED = 5
BALL_SPEED_X, BALL_SPEED_Y = 4, 4
FONT = pygame.font.SysFont("Arial", 40)

# Set up display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Ping Pong Game")

# Paddle positions
left_paddle = pygame.Rect(30, HEIGHT//2 - PADDLE_HEIGHT//2, PADDLE_WIDTH, PADDLE_HEIGHT)
right_paddle = pygame.Rect(WIDTH-40, HEIGHT//2 - PADDLE_HEIGHT//2, PADDLE_WIDTH, PADDLE_HEIGHT)
ball = pygame.Rect(WIDTH//2 - BALL_SIZE//2, HEIGHT//2 - BALL_SIZE//2, BALL_SIZE, BALL_SIZE)

# Scores
score_left = 0
score_right = 0

# Ball direction
ball_dx = BALL_SPEED_X
ball_dy = BALL_SPEED_Y

# Sound setup - Load sounds once at startup
try:
    paddle_hit_sound = pygame.mixer.Sound("ping-pong-64516.mp3")
    other_sound = pygame.mixer.Sound("23lostbutw_iCSUTgIG.mp3")
    other_sound.set_volume(0.3)  # Lower volume (30%)
except:
    # Create dummy sound objects if files not found
    paddle_hit_sound = pygame.mixer.Sound(buffer=bytearray())
    other_sound = pygame.mixer.Sound(buffer=bytearray())

def play_paddle_hit_sound():
    paddle_hit_sound.play()

def play_other_sound():
    other_sound.play()

clock = pygame.time.Clock()

def draw_dashed_line():
    for y in range(0, HEIGHT, 20):
        pygame.draw.rect(screen, WHITE, (WIDTH//2 - 2, y, 4, 10))

def draw_borders():
    for x in range(0, WIDTH, 20):
        pygame.draw.rect(screen, WHITE, (x, 0, 10, 4))
        pygame.draw.rect(screen, WHITE, (x, HEIGHT-4, 10, 4))

def reset_ball():
    global ball, ball_dx, ball_dy
    ball.x = WIDTH//2 - BALL_SIZE//2
    ball.y = HEIGHT//2 - BALL_SIZE//2
    ball_dx *= -1

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # Key Presses
    keys = pygame.key.get_pressed()
    if keys[pygame.K_w] and left_paddle.top > 0:
        left_paddle.y -= PADDLE_SPEED
    if keys[pygame.K_s] and left_paddle.bottom < HEIGHT:
        left_paddle.y += PADDLE_SPEED
    if keys[pygame.K_UP] and right_paddle.top > 0:
        right_paddle.y -= PADDLE_SPEED
    if keys[pygame.K_DOWN] and right_paddle.bottom < HEIGHT:
        right_paddle.y += PADDLE_SPEED

    # Move Ball
    ball.x += ball_dx
    ball.y += ball_dy

    # Collisions
    if ball.top <= 0 or ball.bottom >= HEIGHT:
        ball_dy *= -1
        play_other_sound()
    if ball.colliderect(left_paddle) or ball.colliderect(right_paddle):
        ball_dx *= -1
        play_paddle_hit_sound()

    # Score
    if ball.left <= 0:
        score_right += 1
        play_other_sound()
        reset_ball()
    if ball.right >= WIDTH:
        score_left += 1
        play_other_sound()
        reset_ball()

    # Drawing
    screen.fill(BLACK)
    draw_borders()
    draw_dashed_line()
    pygame.draw.rect(screen, WHITE, left_paddle)
    pygame.draw.rect(screen, WHITE, right_paddle)
    pygame.draw.ellipse(screen, WHITE, ball)
    score_text = FONT.render(f"{score_left}   {score_right}", True, WHITE)
    screen.blit(score_text, (WIDTH//2 - score_text.get_width()//2, 20))

    pygame.display.flip()
    clock.tick(60) 