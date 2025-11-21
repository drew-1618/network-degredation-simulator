# game constants
WIDTH, TOTAL_HEIGHT = 800, 750
CONTROL_PANEL_HEIGHT = 150
HEIGHT = TOTAL_HEIGHT - CONTROL_PANEL_HEIGHT
FPS = 60
PAUSE_DURATION = 1000  # 1 seconds delay
FLASH_DURATION = 400   # 200 ms flash
VISUAL_LOSS_INTERVAL = 500  # check visual loss every 500 ms (2 checks/s)
AI_REACTION_TIME = 200  # 200 ms to make AI beatable with no degradation
MAX_SCORE = 5

# in ms: additional fluctuation around the latency slider value 
# key:value format -> latency from slider : additional jitter 
JITTER_MAP = {
    0 : 0,
    1 : 1,
    10 : 2,
    45 : 10,
    100 : 30,
    300 : 80,
    600 : 150
}

# preset options to mimic real scenarios
# scaled down from real-world avergages 
PRESET_MAP = {
    'LAN' : {'latency' : 1, 'loss' : 0.0},
    'Wi-Fi' : {'latency' : 15, 'loss' : 0.1},
    '4G LTE' : {'latency' : 80, 'loss' : 1.0},
    # Geo-satellite
    'Sat' : {'latency' : 400, 'loss' : 3.0},
}

# preset buttons
PRESET_Y = 80
PRESET_WIDTH = 75
PRESET_HEIGHT = 30
GAP = 20

# slider
SLIDER_Y = 30
SLIDER_X_START = 50
SLIDER_SPACING = 300
SLIDER_WIDTH = 200

# button
BUTTON_WIDTH = 130
BUTTON_HEIGHT = 40
BUTTON_X = 45  # right of control panel
BUTTON_Y = 80

# colors
WHITE = (255, 255, 255)
BLACK = (15, 15, 20)
RED = (239, 83, 80)
GREEN = (102, 187, 106)
BLUE = (25, 118, 210)
DARKER_BLUE = (30, 60, 150)  # for button hover (start/pause)
DARK_GREEN = (56, 142, 60)  # for button hover (play again)
GRAY = (100, 100, 100)
DARK_GRAY = (55, 55, 60)
CONTROL_CENTER_BLUE = (28, 32, 42)

# component constants
PADDLE_WIDTH, PADDLE_HEIGHT = 15, 100
PADDLE_SPEED = 8
BALL_SIZE = 15
BALL_SPEED = 4
BALL_SPEED_INCREMENT = 0.2