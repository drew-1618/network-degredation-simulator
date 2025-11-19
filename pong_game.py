import pygame
import random
import sys

from config import *
from components.paddle import Paddle
from components.ball import Ball

# game set up
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Network Degradation Pong Simulator")
clock = pygame.time.Clock()
# font for scores and messages
font = pygame.font.Font(None, 74)

# object instantiations
# player is left paddle
player_paddle = Paddle(50, (HEIGHT // 2 - PADDLE_HEIGHT // 2), PADDLE_SPEED)
# ai is right paddle
ai_paddle = Paddle((WIDTH - PADDLE_WIDTH - 50), (HEIGHT // 2 - PADDLE_HEIGHT // 2), PADDLE_SPEED)
ball = Ball((WIDTH // 2 - BALL_SIZE // 2), (HEIGHT // 2 - BALL_SIZE / 2), BALL_SPEED)

# score tracking
player_score = 0
ai_score = 0

# game state 
game_paused = False
game_paused_timer = 0

# visual state
hit_flash = False
hit_flash_timer = 0
score_flash = False
score_flash_timer = 0

def handle_input():
    """Handle all user input for player and quitting game"""
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    keys = pygame.key.get_pressed()

    # player movement
    if keys[pygame.K_UP]:
        player_paddle.move(-1)
    if keys[pygame.K_DOWN]:
        player_paddle.move(1)

def ai_movement(paddle, ball):
    """Implement a simple and perfect AI player"""
    # determine difference from ai paddle and ball
    center_diff = ball.centery - paddle.centery

    # check if ball is below paddle center
    if center_diff > 0:
        # move down with a limit of the speed
        paddle.y += min(paddle.speed, center_diff)
    # check if ball is above paddle center
    elif center_diff < 0:
        # move up with a limit of the speed
        paddle.y -= min(paddle.speed, abs(center_diff))
    
    # boundary check to not go off screen
    if paddle.top < 0:
        paddle.top = 0
    if paddle.bottom > HEIGHT:
        paddle.bottom = HEIGHT

def check_collision():
    """Handle ball collisions with walls and paddles"""
    global player_score, ai_score, game_paused, game_paused_timer
    global hit_flash, hit_flash_timer, score_flash, score_flash_timer

    # top & bottom wall collision
    if ball.top <= 0 or ball.bottom >= HEIGHT:
        ball.velocity_y *= -1
    # paddle collision with ball
    if ball.colliderect(player_paddle) or ball.colliderect(ai_paddle):
        ball.velocity_x *= -1

    # scoring (left & right walls)
    # ball passed left paddle, AI scores
    if ball.left <= 0:
        ai_score += 1
        ball.reset()

        # activate pause
        game_paused = True
        game_paused_timer = pygame.time.get_ticks()

        # activate red flash
        hit_flash = True
        hit_flash_timer = pygame.time.get_ticks()

    # ball passed right paddle, player scores
    if ball.right >= WIDTH:
        player_score += 1
        ball.reset()

        # activate pause
        game_paused = True
        game_paused_timer = pygame.time.get_ticks()

        # activate green flash
        hit_flash = True
        hit_flash_timer = pygame.time.get_ticks()

def draw_elements():
    """Draw all game elements & scores onto screen"""
    global hit_flash, score_flash

    background_color = BLACK  # default
    if hit_flash:
        background_color = RED
    elif score_flash:
        background_color = GREEN

    screen.fill(background_color)
    # draw paddles & ball
    pygame.draw.rect(screen, WHITE, player_paddle)
    pygame.draw.rect(screen, WHITE, ai_paddle)
    pygame.draw.rect(screen, WHITE, ball)

    # draw dividing line
    pygame.draw.aaline(screen, WHITE, (WIDTH // 2, 0), (WIDTH // 2, HEIGHT))

    # render scores
    player_text = font.render(str(player_score), True, WHITE)
    ai_text = font.render(str(ai_score), True, WHITE)
    screen.blit(player_text, (WIDTH // 2 - 60, 20))
    screen.blit(ai_text, (WIDTH // 2 + 30, 20))

    pygame.display.flip()

def game_loop():
    global game_paused, game_paused_timer
    global hit_flash, hit_flash_timer, score_flash, score_flash_timer
    running = True
    while running:
        handle_input()

        # pause game
        if game_paused:
            time_now = pygame.time.get_ticks()
            if time_now - game_paused_timer > PAUSE_DURATION:
                game_paused = False

        # flash red
        if hit_flash:
            time_now = pygame.time.get_ticks()
            if time_now - hit_flash_timer > FLASH_DURATION:
                hit_flash = False
        # flash green
        if score_flash:
            time_now = pygame.time.get_ticks()
            if time_now - score_flash_timer > FLASH_DURATION:
                score_flash = False

        if not game_paused:
            ball.move()
            check_collision()
            ai_movement(ai_paddle, ball)

        draw_elements()
        clock.tick(FPS)

if __name__ == "__main__":
    game_loop()
    