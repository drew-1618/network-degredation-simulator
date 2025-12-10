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
pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((WIDTH, TOTAL_HEIGHT))
pygame.display.set_caption("Network Degradation Pong Simulator")
clock = pygame.time.Clock()
# font for scores and messages
font = pygame.font.Font(None, 74)
small_font = pygame.font.Font(None, 24)

def load_sound(filename):
    try:
        return pygame.mixer.Sound(filename)
    except FileNotFoundError:
        print(f"Warning: Could not load {filename}. Sound will be disabled.")
        return None

# load audio files
sfx_ai_scored = load_sound("audio_files/ai_scored.wav")
sfx_background_music = load_sound("audio_files/background_music.wav")
sfx_paddle_hit = load_sound("audio_files/paddle_hit.wav")
sfx_player_scored = load_sound("audio_files/player_scored.wav")

if sfx_background_music:
    sfx_background_music.play(-1)
    sfx_background_music.set_volume(0.3)

# object instantiations
# player is left paddle
player_paddle = Paddle(50, (HEIGHT // 2 - PADDLE_HEIGHT // 2) + CONTROL_PANEL_HEIGHT, PADDLE_SPEED)
# ai is right paddle
ai_paddle = Paddle((WIDTH - PADDLE_WIDTH - 50), (HEIGHT // 2 - PADDLE_HEIGHT // 2) + CONTROL_PANEL_HEIGHT, PADDLE_SPEED)
ball = Ball((WIDTH // 2 - BALL_SIZE // 2), (HEIGHT // 2 - BALL_SIZE / 2) + CONTROL_PANEL_HEIGHT, BALL_SPEED)

# init degradation engine
engine = DegradationEngine(player_paddle, ai_paddle)
engine.set_parameters(0, 0)

# create sliders
latency_slider = Slider(SLIDER_X_START, SLIDER_Y, SLIDER_WIDTH, 50, 0, 500, "Latency (ms)")
loss_slider = Slider(SLIDER_X_START + SLIDER_SPACING, SLIDER_Y, SLIDER_WIDTH, 50, 0, 100, "Avg Packet loss (%)")
sliders = [latency_slider, loss_slider]

# create start, pause, play again button
start_pause_button = Button(BUTTON_X, BUTTON_Y, BUTTON_WIDTH, BUTTON_HEIGHT, "START", BLUE)

# create mute button for background music
mute_button = Button(MUTE_BTN_X, MUTE_BTN_Y, MUTE_BTN_W, 30, "MUTE", GRAY)

# create buttons for scenarios
preset_buttons = []
preset_keys = list(PRESET_MAP.keys())
for i, key in enumerate(preset_keys):
    x_pos = 210 + (i * (PRESET_WIDTH + GAP))
    btn = Button(x_pos, PRESET_Y, PRESET_WIDTH, PRESET_HEIGHT, key, GRAY)
    preset_buttons.append(btn)

# score tracking
player_score = 0
ai_score = 0

# game state 
game_paused = False
game_paused_timer = 0
reset_stats_pending = False
is_game_running = False
is_game_over = False
is_muted = False

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

def set_scenario(preset_name):
    """Update sliders and engine to match preset chosen"""
    data = PRESET_MAP[preset_name]
    # force update to sliders visually
    latency_slider.set_value(data['latency'])
    loss_slider.set_value(data['loss'])
    # apply to engine
    engine.set_parameters(data['latency'], data['loss'])

def toggle_game_state():
    """Helper to toggle start/pause/reset"""
    global is_game_running, is_game_over, player_score, ai_score, game_paused
    
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
    
def handle_input():
    """Handle all user input for player, sliders, and quitting game"""
    global game_paused, is_game_over, is_game_running, ai_score, player_score, is_muted

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        # handle start/pause button with keyboard
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                toggle_game_state()

        # handle start/pause button with mouse
        if start_pause_button.handle_click(event):
            toggle_game_state()

        # handle mute button
        if mute_button.handle_click(event):
            is_muted = not is_muted
            if is_muted:
                mute_button.text = "UNMUTE"
                if sfx_background_music:
                    sfx_background_music.set_volume(0.0)
            else:
                mute_button.text = "MUTE"
                if sfx_background_music:
                    sfx_background_music.set_volume(0.5)

        # handle scenario buttons
        if not is_game_over:
            for btn in preset_buttons:
                if btn.handle_click(event):
                    for b in preset_buttons:
                        b.active = False  # reset all buttons
                    btn.active = True     # set clicked button active
                    set_scenario(btn.text)

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

    hit_occurred = False
    # paddle collision with ball
    if ball.colliderect(player_paddle) and ball.velocity_x < 0:
        ball.velocity_x *= -1
        hit_occurred = True
    if ai_paddle.colliderect(ball) and ball.velocity_x > 0:
        ball.velocity_x *= -1
        hit_occurred = True

    # play paddle hit audio
    if hit_occurred and sfx_paddle_hit:
        sfx_paddle_hit.play()

    score_occurred = False
    # scoring (left & right walls)
    # ball passed left paddle, AI scores
    if ball.left <= 0:
        ai_score += 1
        score_occurred = True
        if sfx_ai_scored:
            sfx_ai_scored.play()

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
        if sfx_player_scored: 
            sfx_player_scored.play()

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
    pygame.draw.rect(screen, CONTROL_CENTER_BLUE, (0, 0, WIDTH, CONTROL_PANEL_HEIGHT))
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

    # draw presets
    for btn in preset_buttons:
        btn.draw(screen)

    # draw mute
    mute_button.draw(screen)

    # get & display stats
    stats = engine.get_stats()
    # only show live stats during game
    if not is_game_over:
        rate_text = small_font.render(f"Actual Loss Rate: {stats['loss rate']:.1f}%", True,
                                        RED if stats['loss rate'] > 0 else GREEN)
        screen.blit(rate_text, (600, 20))
        total_count_text = small_font.render(f"Sent: {stats['sent']}", True, WHITE)
        screen.blit(total_count_text, (600, 45))
        received_count_text = small_font.render(f"Received: {stats['received']}", True, GREEN)
        screen.blit(received_count_text, (600, 70))
        lost_count_text = small_font.render(f"Lost: {stats['lost']}", True, RED)
        screen.blit(lost_count_text, (600, 95))

    # draw buttons
    if is_game_over:
        start_pause_button.text = "PLAY AGAIN"
        start_pause_button.color = GREEN
    else:
        start_pause_button.text = "PAUSE" if is_game_running else "START"
        start_pause_button.color = BLUE
    start_pause_button.draw(screen)

    # draw paddles & ball
    pygame.draw.rect(screen, WHITE, player_paddle)
    pygame.draw.rect(screen, WHITE, ai_paddle)
    if ball_visible:
        pygame.draw.ellipse(screen, WHITE, ball)

    # draw dividing line
    pygame.draw.aaline(screen, WHITE, (WIDTH // 2, CONTROL_PANEL_HEIGHT), (WIDTH // 2, TOTAL_HEIGHT))

    # draw  player labels
    label_player = small_font.render("PLAYER", True, GRAY)
    label_ai = small_font.render("COMPUTER", True, GRAY)
    # Left side (Player)
    screen.blit(label_player, label_player.get_rect(center=(WIDTH // 4, CONTROL_PANEL_HEIGHT + 20)))
    # Right side (Computer)
    screen.blit(label_ai, label_ai.get_rect(center=(3 * WIDTH // 4, CONTROL_PANEL_HEIGHT + 20)))

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
        screen.blit(game_over_text, game_over_text.get_rect(center=(WIDTH/2, CONTROL_PANEL_HEIGHT + 160)))
        
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

        # only if manually started and not paused between scores
        if is_game_running and not game_paused:
            ball.move()
            check_collision()
            ai_movement(ai_paddle, ball)
            apply_lagged_actions()

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

        draw_elements()
        clock.tick(FPS)

if __name__ == "__main__":
    game_loop()
    