SCREEN_SIZE = (1200, 900)
ICON = 'Lobster.png'
CAPTION = 'Lobster-Remake'
FPS = 60
TILE_SIZE = 96
IMAGE_PATH = "assets/images"
MAP_PATH = "assets/maps"
MUSIC_PATH = "assets/music"
SOUND_PATH = "assets/sounds"

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
DEFAULT_HEALTH_REGEN = 0

# Staminaized interface
DEFAULT_STAMINA = 0
DEFAULT_MAX_STAMINA = 100
DEFAULT_STAMINA_REGEN = 25

# Manaized interface
DEFAULT_MANA = 100
DEFAULT_MAX_MANA = 100
DEFAULT_MANA_REGEN = 10

# Attackable interface
DEFAULT_ATTACK_DAMAGE = 40
DEFAULT_ATTACK_RANGE = TILE_SIZE // 2
DEFAULT_ATTACK_SPEED = 1  # attacks per sec
DEFAULT_BASIC_ATTACK_COST = 45  # stamina consumed per attack

# SpellCastable interface
DEFAULT_ABILITY_POWER = 30
DEFAULT_ABILITY_COOLDOWN = 3
DEFAULT_ABILITY_STAMINA_COST = 40
DEFAULT_ABILITY_MANA_COST = 30

# ExplosionProjectileCastable interface
DEFAULT_EXPLOSION_DIAMETER = TILE_SIZE
DEFAULT_PROJECTILE_SPEED = 10
