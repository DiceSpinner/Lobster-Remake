SCREEN_SIZE = (1200, 900)
ICON = 'Lobster.png'
CAPTION = 'Lobster Remake'
FPS = 60
TILE_SIZE = 96
IMAGE_PATH = "assets/images"
MAP_PATH = "assets/maps"
MUSIC_PATH = "assets/music"
SOUND_PATH = "assets/sounds"

SQUARE = 'square'
CIRCLE = 'circle'
SHAPES = [SQUARE, CIRCLE]

PLACE_HOLDER = 'self.'
EMPTY_CONDITION = 'empty'

# surrounding detection
DEFAULT_DETECTION_RADIUS = 1

# particle attributes
DEFAULT_DISPLAY_PRIORITY = 0
DEFAULT_PARTICLE_TEXTURE = "Lobster_64.png"
DEFAULT_PARTICLE_NAME = "particle"  # used while not reading data from map files

# Living interface
DEFAULT_HEALTH = 100
DEFAULT_MAX_HEALTH = 100
DEFAULT_HEALTH_REGEN = 10

# Staminaized interface
DEFAULT_STAMINA = 100
DEFAULT_MAX_STAMINA = 100
DEFAULT_STAMINA_REGEN = 25

# Manaized interface
DEFAULT_MANA = 100
DEFAULT_MAX_MANA = 100
DEFAULT_MANA_REGEN = 20

# StandardAttacks interface
DEFAULT_ATTACK_DAMAGE = 40
DEFAULT_ATTACK_RANGE = TILE_SIZE // 2
DEFAULT_ATTACK_SPEED = 1  # attacks per sec
DEFAULT_ATTACK_STAMINA_COST = 45  # stamina consumed per attack
DEFAULT_ATTACK_MANA_COST = 0
DEFAULT_TARGET = "( not id = self.id )"
BASIC_ATTACK_TEXTURE = 'attack_circle.png'

# SpellCastable interface
DEFAULT_ABILITY_POWER = 30
DEFAULT_ABILITY_COOLDOWN = 0.1
DEFAULT_ABILITY_STAMINA_COST = 0
DEFAULT_ABILITY_MANA_COST = 0

# ExplosionProjectileCastable interface
DEFAULT_PROJECTILE_COUNTDOWN = FPS * 2  # 2 secs before self-destruction
DEFAULT_PROJECTILE_SPEED = 600
FIREBALL_EXPLOSION_RANGE = TILE_SIZE // 2
FIREBALL_TEXTURE = 'fireball.png'
FIREBALL_BRIGHTNESS = 150
