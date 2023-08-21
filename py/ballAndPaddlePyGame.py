import pygame
import sys

# Define some colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Define some dimensions
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
BALL_SIZE = 20
PADDLE_WIDTH = 100
PADDLE_HEIGHT = 20
PADDLE_SPEED = 2
BALL_SPEED = 2

# Initialize Pygame
pygame.init()

# Set the size of the window
window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))

# Create a paddle
paddle = pygame.Rect(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 50, PADDLE_WIDTH, PADDLE_HEIGHT)

# Create a ball
ball = pygame.Rect(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2, BALL_SIZE, BALL_SIZE)
ball_dx = BALL_SPEED
ball_dy = BALL_SPEED

# Game loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
    
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        paddle.move_ip(-PADDLE_SPEED, 0)
        if paddle.left < 0:
            paddle.left = 0
    if keys[pygame.K_RIGHT]:
        paddle.move_ip(PADDLE_SPEED, 0)
        if paddle.right > WINDOW_WIDTH:
            paddle.right = WINDOW_WIDTH
    
    ball.move_ip(ball_dx, ball_dy)
    if ball.left < 0 or ball.right > WINDOW_WIDTH:
        ball_dx *= -1
    if ball.top < 0 or ball.colliderect(paddle):
        ball_dy *= -1
    if ball.bottom > WINDOW_HEIGHT:
        pygame.quit()
        sys.exit()
    
    window.fill(BLACK)
    pygame.draw.rect(window, WHITE, paddle)
    pygame.draw.rect(window, WHITE, ball)
    pygame.display.flip()
    pygame.time.Clock().tick(60)
