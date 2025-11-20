# game constants
WIDTH, TOTAL_HEIGHT = 800, 700
CONTROL_PANEL_HEIGHT = 100
HEIGHT = TOTAL_HEIGHT - CONTROL_PANEL_HEIGHT
FPS = 60
PAUSE_DURATION = 1000  # 1 seconds delay
FLASH_DURATION = 200   # 200 ms flash
VISUAL_LOSS_INTERVAL = 500  # check visual loss every 500 ms (2 checks/s)
AI_REACTION_TIME = 100  # 100 ms to make AI beatable with no degradation

# in ms: additional fluctuation around the latency slider value 
# key:value format -> latency from slider : additional jitter 
JITTER_MAP = {
    0 : 0,
    10 : 2,
    50 : 10,
    150 : 30,
    300 : 80
}

# slider
SLIDER_Y = 30
SLIDER_X_START = 50
SLIDER_SPACING = 300
SLIDER_WIDTH = 200

# colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (244, 67, 54)
GREEN = (76, 175, 80)
BLUE = (100, 100, 255)

# component constants
PADDLE_WIDTH, PADDLE_HEIGHT = 15, 100
PADDLE_SPEED = 8
BALL_SIZE = 15
BALL_SPEED = 4
BALL_SPEED_INCREMENT = 0.2