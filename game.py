import math
import pygame
from effect import *
from particles import *
from Creatures import NPC, Player
from utilities import Positional, Staminaized, BufferedStats, UpdateReq
from bool_expr import BoolExpr
from predefined_particle import PredefinedParticle
from settings import *
from data_structures import PriorityQueue
from error import CollidedParticleNameError
import os


class GameMap:
    """
    Description: Game map object
    === Public Attributes ===
    name: name of the map
    tile_size: the size of each tile in pixels
    height: height of the map (in tiles)
    width: width of the map (in tiles)
    all_particles: All particles on this map
    content: All particles on this map stored in map format
    tiles: All tiles on this map
    """
    name: str
    tile_size: int
    width: int
    height: int
    all_particles: set[int]
    content: List[List[Set[int]]]
    tiles: List[List[int]]

    def __init__(self, location: str,
                 look_up: dict[str, PredefinedParticle]) -> None:
        self.tile_size = TILE_SIZE
        with open(location, 'r') as file:
            lines = file.readlines()
            info = lines[0].split(" ")
            self.name = info[0]
            self.width = int(info[1])
            self.height = int(info[2])
            rows = lines[1:]
            self.all_particles = set()
            self.content = [[set() for j in range(self.width)]
                            for i in range(self.height)]
            self.tiles = [[-1 for j in range(self.width)]
                          for i in range(self.height)]
            Particle.game_map[self.name] = self.content
            Particle.tile_map[self.name] = self.tiles
            for i in range(len(rows)):
                pos_y = i * TILE_SIZE
                row = rows[i].rstrip()
                row = row.split("	")
                for j in range(len(row)):
                    pos_x = j * TILE_SIZE
                    col = row[j].split('_')
                    for particle in col:
                        pre_p = look_up[particle]
                        pre_p.info['x'] = pos_x
                        pre_p.info['y'] = pos_y
                        pre_p.info['map_name'] = self.name
                        particle_class = globals()[pre_p.info['class']]
                        particle = particle_class(pre_p.info.copy())
                        if isinstance(particle, Block):
                            self.tiles[i][j] = particle.id

    def update_contents(self) -> None:
        for particle in self.all_particles.copy():
            if particle not in Particle.particle_group or \
                    not Particle.particle_group[particle].map_name == self.name:
                self.all_particles.remove(particle)

        for new_particle in Particle.new_particles.copy():
            p = Particle.particle_group[new_particle]
            if p.map_name == self.name:
                self.all_particles.add(p.id)
            Particle.new_particles.pop(new_particle, None)


class Camera(Positional):
    """
    Camera used to display player/particle movements
    === Public Attributes ===
    - game_maps: game maps this camera operates on
    - length: length of the camera in pixels
    - width: width of the camera in pixels
    - particle: the particle to be focused on
    - max_x: max x-coordinate of the camera on the current map
    - max_y: max y-coordinate of the camera on the current map
    - min_x: minimum y-coordinate of the camera on the current map
    - min_y: minimum y-coordinate of the camera on the current map
    """
    shades = {}
    game_maps: dict[str, GameMap]
    height: int
    width: int
    particle: Particle
    max_x: int
    max_y: int
    min_x: int
    min_y: int

    def __init__(self, particle: Particle,
                 height: int, width: int,
                 game_maps: dict[str, GameMap]) -> None:
        Positional.__init__(self, **{"map_name": particle.map_name})
        self.particle = particle
        self.game_maps = game_maps
        self.width = width
        self.height = height
        self.min_x = 0
        self.min_y = 0
        self.sync()

    def sync(self):
        """
        Synchronize the position of this camera with the particle
        """
        self.map_name = self.particle.map_name
        radius = self.particle.diameter / 2
        self.x = self.particle.x + radius - self.width / 2 / Particle.Scale
        self.y = self.particle.y + radius - self.height / 2 / Particle.Scale
        current_map = self.game_maps[self.map_name]
        self.max_x = current_map.width * TILE_SIZE - math.ceil(self.width /
                                                               Particle.Scale)
        self.max_y = current_map.height * TILE_SIZE - math.ceil(self.height /
                                                                Particle.Scale)
        if self.x > self.max_x:
            self.x = self.max_x
        elif self.x < self.min_x:
            self.x = self.min_x
        if self.y > self.max_y:
            self.y = self.max_y
        elif self.y < self.min_y:
            self.y = self.min_y

    def get_displaying_particles(self) -> Tuple[Set[Tuple[int, float, float]],
                                                Set[Tuple[
                                                    Tuple[float, float], int]]]:
        size = math.ceil(TILE_SIZE * Particle.Scale)
        current_map = self.game_maps[self.map_name]
        displaying = set()
        start_row = int(self.y // TILE_SIZE)
        first_tile_pixel_y = math.ceil((self.y - start_row * TILE_SIZE) *
                                       Particle.Scale)
        offset_y = size - first_tile_pixel_y
        end_row = start_row + math.ceil((self.height - offset_y) / size)
        start_col = int(self.x // TILE_SIZE)
        first_tile_pixel_x = math.ceil((self.x - start_col * TILE_SIZE) *
                                       Particle.Scale)
        offset_x = size - first_tile_pixel_x
        end_col = start_col + math.ceil((self.width - offset_x) / size)
        shades = set()
        in_queue = set()
        begin_x = -first_tile_pixel_x
        begin_y = -first_tile_pixel_y
        # add tiles & entities to the queue
        row_count = 0
        for i in range(start_row, end_row + 1):
            col_count = 0
            for j in range(start_col, end_col + 1):
                ps = current_map.content[i][j]
                for idti in ps:
                    if idti in in_queue:
                        continue
                    in_queue.add(idti)
                    item = Particle.particle_group[idti]
                    block_x = begin_x + col_count * size
                    block_y = begin_y + row_count * size
                    if isinstance(item, Block):
                        display_x = block_x
                        display_y = block_y
                        brightness = item.get_stat("brightness")
                        if brightness > 0:
                            displaying.add((idti, display_x, display_y))
                        shades.add(((display_x, display_y), 255 -
                                    brightness))
                    else:
                        bx = j * TILE_SIZE
                        by = i * TILE_SIZE
                        display_x = block_x + (item.x - bx) * Particle.Scale
                        display_y = block_y + (item.y - by) * Particle.Scale
                        flag = False
                        tiles = item.get_tiles_in_contact()
                        for t in tiles:
                            if t.get_stat("brightness") > 0:
                                flag = True
                        if flag:
                            displaying.add((idti, display_x, display_y))
                col_count += 1
            row_count += 1
        return displaying, shades

    def display(self, screen: pygame.Surface):
        """ Display the content onto the screen by their priority
        """
        displaying, shades = self.get_displaying_particles()
        queue = PriorityQueue(lower_priority_over_id)
        new_dict = {}
        for item in displaying:
            new_dict[item[0]] = (item[1], item[2])
        # display items by their priority
        for item in new_dict:
            queue.enqueue(Particle.particle_group[item])
        while not queue.is_empty():
            item = queue.dequeue()
            item.display(screen, new_dict[item.id])
        # display brightness
        for s in shades:
            location = s[0]
            shade = get_shade(s[1])
            screen.blit(shade, location)


class Level:
    """
    Description: Levels of the game

    === Public Attributes ===
    difficulty: difficulty of the level
    goal: The goal of the level
    running: Whether this level is running

    === Private Attributes ===
    _game_maps: Loaded game maps, accessed by their names
    _map_names: Name of the maps
    _particle_names: Names of the file that stores predefined particles info
    _camera: Camera for this level
    _initialized: Whether the level has been initialized

    === Representation Invariants ===
    - difficulty must be an integer from 0 - 3
    """
    difficulty: int
    goal: BoolExpr
    _game_maps: dict[str, GameMap]
    _camera: Camera
    _map_names: List[str]
    _particle_names: List[str]
    _initialized: bool
    running: bool
    fonts: dict[str, pygame.font.Font]
    texts: dict[str, pygame.Surface]

    def __init__(self, asset: List[str]) -> None:
        self._map_names = []
        self._particle_names = []
        for line in asset:
            line = line.rstrip().split('=')
            if line[0] == 'maps':
                self._map_names = line[1].split(':')
            elif line[0] == 'pre_particles':
                self._particle_names.append(line[1])
        self.difficulty = 0  # default difficulty
        self._initialized = False
        self._game_maps = {}
        self.fonts = {}
        self.texts = {}
        self.running = False

    def _load_maps(self) -> None:
        # load in predefined particles
        look_up = {}
        for name in self._particle_names:
            path = os.path.join("Predefined Particles", name)
            particles = os.listdir(path)
            for particle in particles:
                pre_p = PredefinedParticle(os.path.join(path, particle))
                if pre_p.info['map_display'] not in look_up:
                    look_up[pre_p.info['map_display']] = pre_p
                else:
                    raise CollidedParticleNameError

        for m in self._map_names:
            name = os.path.join("assets/maps", m + ".txt")
            game_map = GameMap(name, look_up)
            self._game_maps[game_map.name] = game_map

    def _load_texts(self):
        self.fonts['player_info'] = pygame.font.Font(None, 25)
        self.texts['health_bar'] = self.fonts[
            'player_info'].render("Health", True, (255, 255, 0))
        self.texts['resource_bar'] = self.fonts[
            'player_info'].render("Mana", True, (0, 100, 255))
        self.texts['stamina_bar'] = self.fonts[
            'player_info'].render("Stamina", True, (0, 255, 0))

    def run(self, screen: pygame.Surface, difficulty=0):
        """
        Run the level with the given setting
        """
        if not self._initialized:
            _load_assets()
            self._load_maps()
            self._load_texts()
            self._initialized = True
            self.running = True
            self.difficulty = difficulty
            player_key = list(Player.player_group)[0]
            player = Player.player_group[player_key]
            # npc_key = list(NPC.npc_group)[0]
            # npc = NPC.npc_group[npc_key]
            self._camera = Camera(player,
                                  screen.get_height(), screen.get_width(),
                                  self._game_maps)
        player_key = list(Player.player_group)[0]
        player = Player.player_group[player_key]
        # mouse tracking
        mouse_pos = pygame.mouse.get_pos()
        pos = Positional()
        pos.x = mouse_pos[0] / Particle.Scale + self._camera.x
        pos.y = mouse_pos[1] / Particle.Scale + self._camera.y
        player.aim(pos)

        # player input and other game actions
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
        pressed_keys = pygame.key.get_pressed()
        if pressed_keys[pygame.K_UP]:
            Particle.Scale += 0.01
            if Particle.Scale > MAX_CAMERA_SCALE:
                Particle.Scale = MAX_CAMERA_SCALE
        if pressed_keys[pygame.K_DOWN]:
            Particle.Scale -= 0.01
            if Particle.Scale < MIN_CAMERA_SCALE:
                Particle.Scale = MIN_CAMERA_SCALE
        active_map = self._game_maps[player.map_name]
        active_particles = get_particles_in_radius(player,
                                                   PARTICLE_UPDATE_RADIUS, None,
                                                   True)
        # particle status update
        tiles = []
        updates = PriorityQueue(lower_update_priority)
        for particle in active_particles:
            if isinstance(particle, ActiveParticle):
                # queue up actions
                particle.action()
            if isinstance(particle, UpdateReq):
                updates.enqueue(particle)
            if isinstance(particle, Block):
                tiles.append(particle)

        # execute particle actions
        for i in range(Staminaized.action_queue.get_size()):
            particle, args, name = Staminaized.action_queue.dequeue()
            particle.execute_action(name, args)
        Staminaized.action_queue.reset()
        while not updates.is_empty():
            updates.dequeue().update_status()
        active_map.update_contents()

        # lighting
        for block in tiles:
            if block.get_stat('light_source') > 0:
                block.light()

        # display
        self._camera.sync()
        self._camera.display(screen)
        self.player_info_display(player, screen)
        # reset buffer
        for particle in Particle.particle_group:
            particle = Particle.particle_group[particle]
            if isinstance(particle, BufferedStats):
                particle.reset()

    def player_info_display(self, player: Player, screen: pygame.Surface):
        health_bar_width = 300
        health_bar_height = 12
        resource_bar_width = 200
        resource_bar_height = 12
        stamina_bar_height = 12
        stamina_bar_width = 250

        health_percent = player.health / player.max_health
        health_bar = pygame.Surface((health_percent * health_bar_width,
                                     health_bar_height))
        health_bar.fill((255, 0, 0))
        screen.blit(self.texts['health_bar'], (80, 60))
        screen.blit(health_bar, (80, 80))

        stamina_percent = player.stamina / player.max_stamina
        stamina_bar = pygame.Surface((stamina_percent * stamina_bar_width,
                                      stamina_bar_height))
        stamina_bar.fill((0, 255, 0))
        screen.blit(self.texts['stamina_bar'], (80, 100))
        screen.blit(stamina_bar, (80, 120))

        mana_percent = player.mana / player.max_mana
        mana_bar = pygame.Surface((mana_percent * resource_bar_width,
                                   resource_bar_height))
        mana_bar.fill((0, 255, 255))
        screen.blit(self.texts['resource_bar'], (80, 140))
        screen.blit(mana_bar, (80, 160))

    def exit(self):
        """
        Release memory of loaded resources and exit the level
        """
        self.difficulty = 0  # reset difficulty
        self._game_maps = {}


class Game:
    """
    Description:
        A game object representing the game the player is playing
    === Private Attributes ===
        _screen: Screen of the game that gets displayed to the player
        _levels: Levels of this game
        _frame_rate: Frame rate of the game
        _level_selecting: whether the game is on title screen
        _level_running: whether the game is running on a level
        _selected_level: Selected level
    """
    _screen: pygame.Surface
    _levels: List[Level]
    _frame_rate: int
    _level_selecting: bool
    _level_running: bool
    _selected_level: int

    def start(self) -> None:
        """
        Initialize the engine and start the game.
        """
        self._level_selecting = True
        self._level_running = False
        self._selected_level = -1
        pygame.init()
        pygame.mixer.init()
        pygame.font.init()
        self._apply_settings()
        self._levels = []
        self._load_level()
        self.run()

    def _apply_settings(self) -> None:
        """
        Apply game gui settings
        """
        pygame.display.set_icon(pygame.image.load(os.path.join("assets", ICON)))
        self._screen = pygame.display.set_mode(SCREEN_SIZE)
        pygame.display.set_caption(CAPTION)
        self.frame_rate = FPS

    def _load_level(self) -> None:
        """
        Load levels from the "Levels" folder into the game.
        """
        levels = os.listdir("Levels")
        for lev in levels:
            with open(os.path.join('Levels', lev), 'r+') as level_file:
                self._levels.append(Level(level_file.readlines()))

    def run(self) -> None:
        clock = pygame.time.Clock()
        running = True
        pygame.mouse.set_visible(False)
        cursor_image = pygame.image.load(os.path.join("assets", "images",
                                                      "cursor.png"))
        cursor_image = pygame.transform.scale(cursor_image, (24, 24))
        while running:
            clock.tick(self.frame_rate)
            self._screen.fill((0, 0, 0))
            if self._level_selecting:
                self._selected_level = 0
                self._level_selecting = False
                self._level_running = True
            elif self._level_running:
                level = self._levels[self._selected_level]
                level.run(self._screen)
                if not level.running:
                    running = False
            self._screen.blit(cursor_image, pygame.mouse.get_pos())
            # FPS
            font = pygame.font.Font(None, 25)
            text = font.render("FPS:" + str(round(clock.get_fps())), True,
                               (255, 255, 255))
            self._screen.blit(text, (0, 0))
            pygame.display.flip()
        pygame.quit()


def higher_id(p1: Particle, p2: Particle) -> bool:
    return p1.id > p2.id


def lower_display_priority(p1: Particle, p2: Particle) -> bool:
    return p1.display_priority < p2.display_priority


def lower_update_priority(p1: UpdateReq, p2: UpdateReq) -> bool:
    return p1.update_priority < p2.update_priority


def lower_priority_over_id(p1: Particle, p2: Particle) -> bool:
    """ Sort by non-decreasing order """
    if p1.display_priority == p2.display_priority:
        return p1.id > p2.id
    return p1.display_priority < p2.display_priority


def _load_assets():
    """ Load in game assets """
    path = "assets/images"
    paths = os.listdir(path)
    for p in paths:
        pic = pygame.image.load(
            os.path.join(path, p)).convert_alpha()
        Particle.raw_textures[p] = pic
        # Loaded textures are being accessed by 4 parameters
        # in the order of name -> size -> direction -> alpha value
        tup = (p, pic.get_size(), 0, 0)
        Particle.textures[tup] = pic
    path = "assets/sounds"
    paths = os.listdir(path)
    for p in paths:
        Particle.sounds[p] = pygame.mixer.Sound(os.path.join(path, p))


def get_shade(alpha: int) -> pygame.Surface:
    """ Return the shade with the given alpha value """
    try:
        return Camera.shades[Particle.Scale][alpha].copy()
    except KeyError:
        size = math.ceil(Particle.Scale * TILE_SIZE)
        surface = pygame.Surface((size, size))
        surface.fill((0, 0, 0))
        surface.set_alpha(alpha)
        try:
            Camera.shades[Particle.Scale][alpha] = surface
        except KeyError:
            Camera.shades[Particle.Scale] = {}
            Camera.shades[Particle.Scale][alpha] = surface
        return surface.copy()
