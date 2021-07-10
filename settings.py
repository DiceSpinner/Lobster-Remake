SCREEN_SIZE = (1200, 900)
ICON = 'Lobster.png'
CAPTION = 'Lobster-Remake'
FPS = 60
TILE_SIZE = 64

SQUARE = 'square'
CIRCLE = 'circle'
SHAPES = [SQUARE, CIRCLE]

# surrounding detection
DEFAULT_DETECTION_RADIUS = 1

# particle attributes
DEFAULT_DISPLAY_PRIORITY = 0
DEFAULT_PARTICLE_TEXTURE = "Lobster_64.png"
DEFAULT_PARTICLE_NAME = "particle"  # used while not reading data from map files

# Living interface
DEFAULT_HEALTH = 100
DEFAULT_MAX_HEALTH = 100

# Attackable interface
DEFAULT_ATTACK_DAMAGE = 40
DEFAULT_ATTACK_RANGE = TILE_SIZE // 2
DEFAULT_ATTACK_SPEED = FPS * 2  # 2 seconds per attack


