import pygame
import random
import sys

from config import *
from components.paddle import Paddle
from components.ball import Ball
from components.slider import Slider
from degradation_engine import DegradationEngine
from components.button import Button

# game set up
pygame.init()
screen = pygame.display.set_mode((WIDTH, TOTAL_HEIGHT))
pygame.display.set_caption("Network Degradation Pong Simulator")
clock = pygame.time.Clock()
# font for scores and messages
font = pygame.font.Font(None, 74)
small_font = pygame.font.Font(None, 24)

# object instantiations
# player is left paddle
player_paddle = Paddle(50, (HEIGHT // 2 - PADDLE_HEIGHT // 2) + CONTROL_PANEL_HEIGHT, PADDLE_SPEED)
# ai is right paddle
ai_paddle = Paddle((WIDTH - PADDLE_WIDTH - 50), (HEIGHT // 2 - PADDLE_HEIGHT // 2) + CONTROL_PANEL_HEIGHT, PADDLE_SPEED)
ball = Ball((WIDTH // 2 - BALL_SIZE // 2), (HEIGHT // 2 - BALL_SIZE / 2) + CONTROL_PANEL_HEIGHT, BALL_SPEED)

# create sliders
latency_slider = Slider(SLIDER_X_START, SLIDER_Y, SLIDER_WIDTH, 50, 0, 500, "Latency (ms)")
loss_slider = Slider(SLIDER_X_START + SLIDER_SPACING, SLIDER_Y, SLIDER_WIDTH, 50, 0, 100, "Packet loss (%)")
sliders = [latency_slider, loss_slider]

# create button
start_pause_button = Button(BUTTON_X, BUTTON_Y, BUTTON_WIDTH, BUTTON_HEIGHT, "START", BLUE)

# init degradation engine
engine = DegradationEngine(player_paddle, ai_paddle)

# score tracking
player_score = 0
ai_score = 0

# game state 
game_paused = False
game_paused_timer = 0
reset_stats_pending = False
is_game_running = False
is_game_over = False

# visual state
hit_flash = False
hit_flash_timer = 0
score_flash = False
score_flash_timer = 0
ball_visible = True
last_visual_loss_check = 0


def update_degradation_params():
    """Read values from sliders to update engine params"""
    latency = latency_slider.get_value()
    loss = loss_slider.get_value()
    engine.set_parameters(latency, loss)

def handle_input():
    """Handle all user input for player, sliders, and quitting game"""
    global game_paused, is_game_over, is_game_running, ai_score, player_score

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        # handle start/pause button
        if start_pause_button.handle_click(event):
            if is_game_over:
                # reset game params for fresh start
                player_score = 0
                ai_score = 0
                ball.speed = BALL_SPEED
                # reset engine
                engine.reset_stats()
                # reset state flags
                is_game_over = False
                is_game_running = True
                game_paused = False
                ball.reset()
            else:
                # if paused, play; if playing, pause
                is_game_running = not is_game_running

        for slider in sliders:
            slider.handle_event(event)

    # only move if not paused
    if is_game_running and not game_paused and not is_game_over:
        keys = pygame.key.get_pressed()

        # player movement
        if keys[pygame.K_UP]:
            engine.queue_input(player_paddle, -PADDLE_SPEED)
        if keys[pygame.K_DOWN]:
            engine.queue_input(player_paddle, PADDLE_SPEED)

def ai_movement(paddle, ball):
    """Implement a simple and perfect AI player"""
    # determine difference from ai paddle and ball
    center_diff = ball.centery - paddle.centery
    target_move = 0

    # check if ball is below paddle center
    if center_diff > 0:
        # move down with a limit of the speed
        target_move = min(paddle.speed, center_diff)
    # check if ball is above paddle center
    elif center_diff < 0:
        # move up with a limit of the speed
        target_move = -min(paddle.speed, abs(center_diff))
    
    engine.queue_input(paddle, target_move)

def apply_lagged_actions():
    """Apply actions released by engine after latency expires"""

    released_actions = engine.get_due_actions()

    for action in released_actions:
        paddle = action['target']
        move_amount = action['data']
        # apply move physically
        paddle.y += move_amount

        # boundary check to not go off screen
        if paddle.top < CONTROL_PANEL_HEIGHT:
            paddle.top = CONTROL_PANEL_HEIGHT
        if paddle.bottom > TOTAL_HEIGHT:
            paddle.bottom = TOTAL_HEIGHT

def check_collision():
    """Handle ball collisions with walls and paddles"""
    global player_score, ai_score, game_paused, game_paused_timer
    global hit_flash, hit_flash_timer, score_flash, score_flash_timer
    global reset_stats_pending, is_game_over, is_game_running

    # top & bottom wall collision
    if ball.top <= CONTROL_PANEL_HEIGHT or ball.bottom >= TOTAL_HEIGHT:
        ball.velocity_y *= -1
    # paddle collision with ball
    if ball.colliderect(player_paddle) or ball.colliderect(ai_paddle):
        ball.velocity_x *= -1

    score_occurred = False

    # scoring (left & right walls)
    # ball passed left paddle, AI scores
    if ball.left <= 0:
        ai_score += 1
        score_occurred = True

        # activate pause
        game_paused = True
        game_paused_timer = pygame.time.get_ticks()

        # activate red flash
        hit_flash = True
        hit_flash_timer = pygame.time.get_ticks()

        reset_stats_pending = True

    # ball passed right paddle, player scores
    if ball.right >= WIDTH:
        player_score += 1
        score_occurred = True
        engine.reset_stats()

        # increase speed if player scores
        ball.increase_speed()

        # activate pause
        game_paused = True
        game_paused_timer = pygame.time.get_ticks()

        # activate green flash
        score_flash = True
        score_flash_timer = pygame.time.get_ticks()

    if score_occurred:
        reset_stats_pending = True
        # check for game over
        if player_score >= MAX_SCORE or ai_score >= MAX_SCORE:
            is_game_over = True
            is_game_running = False
            game_paused = False
        else:
            ball.reset()

def transparent_background(color):
    """Display a semi-transparent background for popup/overlays"""
    # semi-transparent background
    overlay = pygame.Surface((WIDTH, HEIGHT))
    overlay.set_alpha(200)
    overlay.fill(color)
    screen.blit(overlay, (0, CONTROL_PANEL_HEIGHT))


def draw_elements():
    """Draw all game elements, sliders, & scores onto screen"""
    global hit_flash, score_flash, ball_visible, last_visual_loss_check

    background_color = BLACK  # default
    if hit_flash:
        background_color = RED
    elif score_flash:
        background_color = GREEN

    screen.fill(background_color)

    # draw control background & sliders
    pygame.draw.rect(screen, (30, 30, 30), (0, 0, WIDTH, CONTROL_PANEL_HEIGHT))
    pygame.draw.line(screen, WHITE, (0, CONTROL_PANEL_HEIGHT), (WIDTH, CONTROL_PANEL_HEIGHT))

    # handle ball visibility based on packet loss
    time_now = pygame.time.get_ticks()
    if time_now - last_visual_loss_check > VISUAL_LOSS_INTERVAL:
        current_loss_percent = loss_slider.get_value()
        if random.random() * 100 < current_loss_percent:
            ball_visible = False
        else:
            ball_visible = True
        last_visual_loss_check = time_now
    # draw sliders
    for slider in sliders:
        slider.draw(screen)

    # get & display stats
    stats = engine.get_stats()
    # only show live stats during game
    if not is_game_over:
        rate_text = small_font.render(f"Actual Loss Rate: {stats['loss rate']:.1f}%", True,
                                        RED if stats['loss rate'] > 0 else GREEN)
        screen.blit(rate_text, (600, 20))
        total_count_text = small_font.render(f"Sent: {stats['sent']}", True, WHITE)
        screen.blit(total_count_text, (600, 45))
        split_count_text = small_font.render(f"Received: {stats['received']} | Lost: {stats['lost']}", True, WHITE)
        screen.blit(split_count_text, (600, 70))

    # draw buttons
    if is_game_over:
        start_pause_button.text = "PLAY AGAIN"
    else:
        start_pause_button.text = "PAUSE" if is_game_running else "START"
    start_pause_button.draw(screen)

    # draw paddles & ball
    pygame.draw.rect(screen, WHITE, player_paddle)
    pygame.draw.rect(screen, WHITE, ai_paddle)
    if ball_visible:
        pygame.draw.ellipse(screen, WHITE, ball)

    # draw dividing line
    pygame.draw.aaline(screen, WHITE, (WIDTH // 2, CONTROL_PANEL_HEIGHT), (WIDTH // 2, TOTAL_HEIGHT))

    # render scores
    player_text = font.render(str(player_score), True, WHITE)
    ai_text = font.render(str(ai_score), True, WHITE)
    screen.blit(player_text, (WIDTH // 2 - 60, CONTROL_PANEL_HEIGHT + 20))
    screen.blit(ai_text, (WIDTH // 2 + 30, CONTROL_PANEL_HEIGHT + 20))

    # pause overlay button
    if not is_game_running and not is_game_over:
        transparent_background(BLACK)
        pause = font.render("PAUSED", True, WHITE)
        screen.blit(pause, pause.get_rect(center=(WIDTH / 2, TOTAL_HEIGHT / 2)))

    # end of game display
    if is_game_over:
        player_won = player_score > ai_score
        transparent_background(GREEN) if player_won else transparent_background(RED)
        
        game_over_text = font.render("GAME OVER", True, WHITE)
        screen.blit(game_over_text, game_over_text.get_rect(center=(WIDTH/2, CONTROL_PANEL_HEIGHT + 150)))
        
        if player_won:
            result_text = font.render("YOU WON!", True, WHITE)
        else:
            result_text = font.render("COMPUTER WON!", True, WHITE)
        screen.blit(result_text, result_text.get_rect(center=(WIDTH/2, CONTROL_PANEL_HEIGHT + 250)))
        
        final_score_text = font.render(f"Final Score: {player_score} - {ai_score}", True, WHITE)
        screen.blit(final_score_text, final_score_text.get_rect(center=(WIDTH/2, CONTROL_PANEL_HEIGHT + 320)))

    pygame.display.flip()

def game_loop():
    """Main driver of the game"""
    global game_paused, game_paused_timer
    global hit_flash, hit_flash_timer, score_flash, score_flash_timer
    global reset_stats_pending
    running = True
    while running:
        update_degradation_params()
        handle_input()

        # pause game
        if game_paused:
            time_now = pygame.time.get_ticks()
            if time_now - game_paused_timer > PAUSE_DURATION:
                game_paused = False

                # reset stats
                if reset_stats_pending:
                    engine.reset_stats()
                    reset_stats_pending = False
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

        # only if manually started and not paused between scores
        if is_game_running and not game_paused:
            ball.move()
            check_collision()
            ai_movement(ai_paddle, ball)
            apply_lagged_actions()

        draw_elements()
        clock.tick(FPS)

if __name__ == "__main__":
    game_loop()
    