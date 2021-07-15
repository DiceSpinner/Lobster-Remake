import math

import pygame
from effect import *
from particles import *
from utilities import Positional, Movable, Collidable, Attackable, \
    DynamicStats
from bool_expr import BoolExpr
from predefined_particle import PredefinedParticle
from settings import *
from data_structures import PriorityQueue
from math_formula import segment_intersection, line_circle_intersection, \
    point_vec_left, point_vec_right, point_on_segment
import os


class GameMap:
    """
    Description: Game map object
    === Public Attributes ===
    name: name of the map
    tile_size: the size of each tile in pixels
    height: height of the map (in tiles)
    width: width of the map (in tiles)
    blocks: blocks of the map
    entities: creatures and items inside the map
    """
    name: str
    tile_size: int
    width: int
    height: int
    all_blocks: List[Block]
    blocks: List[List[Block]]
    all_entities: List[Union[Creature, Item]]
    entities: List[List[List[Union[Creature, Item]]]]
    collision_boxs: List[List[List[CollisionBox]]]
    all_collision_boxs: List[CollisionBox]

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
            self.blocks = []
            self.entities = []
            self.collision_boxs = []
            self.all_blocks = []
            self.all_entities = []
            self.all_collision_boxs = []
            for i in range(len(rows)):
                pos_y = i * TILE_SIZE
                row = rows[i].rstrip()
                self.blocks.append([])
                self.entities.append([])
                self.collision_boxs.append([])
                row = row.split("	")
                for j in range(len(row)):
                    pos_x = j * TILE_SIZE
                    self.entities[i].append([])
                    self.collision_boxs[i].append([])
                    col = row[j].split('_')
                    for particle in col:
                        pre_p = look_up[particle]
                        pre_p.info['x'] = pos_x
                        pre_p.info['y'] = pos_y
                        pre_p.info['map_name'] = self.name
                        particle_class = globals()[pre_p.info['class']]
                        par = particle_class(pre_p.info)
                        if isinstance(par, Block):
                            self.blocks[i].append(par)
                            self.all_blocks.append(par)
                        elif isinstance(par, Creature) or isinstance(par, Item):
                            self.entities[i][j].append(par)
                            self.all_entities.append(par)
                        else:
                            self.collision_boxs[i][j].append(par)
                            self.all_collision_boxs.append(par)

    def clear_content(self):
        for i in range(self.height):
            for j in range(self.width):
                self.entities[i][j] = []
                self.collision_boxs[i][j] = []

    def update_contents(self):
        self.clear_content()
        ep = []
        cp = []
        for entity in self.all_entities:
            if entity.id not in Particle.particle_group or not \
                    entity.map_name == self.name:
                ep.append(entity)
                continue
            col = int((entity.x - 1 + entity.diameter / 2) // TILE_SIZE)
            row = int((entity.y - 1 + entity.diameter / 2) // TILE_SIZE)
            self.entities[row][col].append(entity)

        for cb in self.all_collision_boxs:
            if cb.id not in Particle.particle_group or not \
                    cb.map_name == self.name:
                cp.append(cb)
                continue
            col = int((cb.x - 1 + cb.diameter / 2) // TILE_SIZE)
            row = int((cb.y - 1 + cb.diameter / 2) // TILE_SIZE)
            self.collision_boxs[row][col].append(cb)
        for item in ep:
            self.all_entities.remove(item)
        for item in cp:
            self.all_collision_boxs.remove(item)

    def update_surroundings(self, particle: Particle) -> None:
        """ Feed the map info to the selected particle """
        if isinstance(particle, Collidable):
            cx = particle.x - 1 + particle.diameter / 2
            cy = particle.y - 1 + particle.diameter / 2
        else:
            cx = particle.x
            cy = particle.y
        col = int(cx // TILE_SIZE)
        row = int(cy // TILE_SIZE)
        start_col = col - particle.detection_radius
        end_col = col + particle.detection_radius
        start_row = row - particle.detection_radius
        end_row = row + particle.detection_radius
        if start_row < 0:
            start_row = 0
        if end_row >= self.height:
            end_row = self.height - 1
        if start_col < 0:
            start_col = 0
        if end_col >= self.width:
            end_col = self.width - 1
        tiles = {}
        entities = {}
        for i in range(start_row, end_row + 1):
            entities[i] = {}
            tiles[i] = {}
            for j in range(start_col, end_col + 1):
                entities[i][j] = self.entities[i][j][:]
                tiles[i][j] = self.blocks[i][j]
        particle.update_surroundings(tiles, entities)


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
        Positional.__init__(self, {"map_name": particle.map_name})
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
        self.x = self.particle.x - self.width / 2
        self.y = self.particle.y - self.height / 2
        if isinstance(self.particle, Creature):
            self.x += self.particle.diameter / 2
            self.y += self.particle.diameter / 2
        current_map = self.game_maps[self.map_name]
        tile_size = current_map.tile_size
        self.max_x = current_map.width * tile_size - self.width
        self.max_y = current_map.height * tile_size - self.height
        if self.x > self.max_x:
            self.x = self.max_x
        elif self.x < self.min_x:
            self.x = self.min_x
        if self.y > self.max_y:
            self.y = self.max_y
        elif self.y < self.min_y:
            self.y = self.min_y

    def display(self, screen: pygame.Surface):
        """ Display the content onto the screen by their priority
        """
        current_map = self.game_maps[self.map_name]
        displaying = {}
        start_row = int(self.x // TILE_SIZE)
        end_row = int(math.ceil((self.x + self.width) / TILE_SIZE))
        start_col = int(self.y // TILE_SIZE)
        end_col = int(math.ceil((self.y + self.height) / TILE_SIZE))
        # add tiles & entities to the queue
        for i in range(start_row, end_row):
            for j in range(start_col, end_col):
                tile = current_map.blocks[j][i]
                items = []
                if tile.get_stat('brightness') > 0:
                    items.append(tile)
                    items += current_map.entities[j][i]
                    items += current_map.collision_boxs[j][i]
                else:
                    tiles = tile.get_adjacent_tiles()
                    for t in tiles:
                        if t.get_stat('brightness') > 0:
                            for entity in current_map.entities[j][i]:
                                if entity.detect_collision(t):
                                    items.append(entity)
                                for cb in current_map.collision_boxs[j][i]:
                                    if cb.detect_collision(t):
                                        items.append(cb)
                            break

                for item in items:
                    display_x = round(item.x - self.x)
                    display_y = round(item.y - self.y)
                    displaying[item.id] = (display_x, display_y)
        queue = PriorityQueue(compare_by_display_priority)

        # display items by their priority
        for key in displaying:
            queue.enqueue(Particle.particle_group[key])
        while not queue.is_empty():
            item = queue.dequeue()
            item.display(screen, displaying[item.id])

        # display brightness
        # font = pygame.font.Font(None, 25)
        for i in range(start_row, end_row):
            for j in range(start_col, end_col):
                tile = current_map.blocks[j][i]
                dark = pygame.Surface((TILE_SIZE,
                                       TILE_SIZE))
                dark.fill((0, 0, 0))
                adjacent = tile.get_adjacent_tiles(True)
                flag = False
                for t in adjacent:
                    if t.get_stat("brightness") > 0:
                        flag = True
                        break
                if tile.get_stat('brightness') > 0 or flag:
                    if tile.get_stat('brightness') > 0:
                        dark.set_alpha(255 - tile.get_stat('brightness'))
                    display_x = round(tile.x - self.x)
                    display_y = round(tile.y - self.y)
                    screen.blit(dark, (display_x, display_y))
                    # num = font.render(str(tile.get_stat('brightness')), True,
                    #                  (255, 255, 0))
                    # screen.blit(num, (display_x + tile.diameter // 3,
                    # display_y + tile.diameter // 3))


class Level:
    """
    Description: Levels of the game
    === Public Attributes ===
    difficulty: difficulty of the level
    goal: The goal of the level
    running: Whether this level is running
    === Private Attributes ===
    _asset: Loaded assets of the game
    _asset_name: The locations of game assets
    _game_maps: Loaded game maps, accessed by their names
    _map_names: Name of the maps
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
    _initialized: bool
    running: bool
    fonts: dict[str, pygame.font.Font]
    texts: dict[str, pygame.Surface]

    def __init__(self, asset: List[str]) -> None:
        for line in asset:
            line = line.split('=')
            if line[0] == 'maps':
                self._map_names = line[1].split(':')
        self.difficulty = 0  # default difficulty
        self._initialized = False
        self._game_maps = {}
        self.fonts = {}
        self.texts = {}
        self.running = False

    def _load_maps(self) -> None:
        # load in predefined particles
        look_up = {}
        with open('predefined-particles.txt', 'r') as file:
            for line in file:
                p = PredefinedParticle(line)
                look_up[p.info['name']] = p

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
        self.texts['stamina'] = self.fonts[
            'player_info'].render("Sta,oma", True, (0, 255, 0))

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
            self._camera = Camera(player,
                                  screen.get_height(), screen.get_width(),
                                  self._game_maps)
        player_key = list(Player.player_group)[0]
        player = Player.player_group[player_key]

        player_input = []

        # mouse tracking
        mouse_pos = pygame.mouse.get_pos()
        pos = Positional({})
        pos.x = mouse_pos[0] + self._camera.x
        pos.y = mouse_pos[1] + self._camera.y
        player.aim(pos)

        # player input and other game actions
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYUP or event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                player_input.append(event)

        # creature actions
        for creature in Creature.creature_group:
            Creature.creature_group[creature].action(player_input)

        # particle status update
        for particle in Particle.particle_group.copy():
            particle = Particle.particle_group[particle]
            if isinstance(particle, Living):
                if particle.is_dead():
                    particle.die()
                    continue
            if isinstance(particle, Item) or isinstance(particle, Creature):
                if particle not in \
                        self._game_maps[particle.map_name].all_entities:
                    self._game_maps[particle.map_name].all_entities.append(
                        particle)
            if isinstance(particle, CollisionBox):
                if particle not in \
                        self._game_maps[particle.map_name].all_collision_boxs:
                    self._game_maps[
                        particle.map_name].all_collision_boxs.append(particle)
            if isinstance(particle, Attackable) or isinstance(particle,
                                                              CollisionBox):
                particle.count()
                if isinstance(particle, CollisionBox):
                    particle.sync()

        # update entity surroundings
        for game_map in self._game_maps:
            self._game_maps[game_map].update_contents()
        for particle in Particle.particle_group:
            particle = Particle.particle_group[particle]
            self._game_maps[particle.map_name].update_surroundings(particle)

        # lighting
        for creature in Creature.creature_group:
            creature = Creature.creature_group[creature]
            if creature.get_stat('light_source') > 0 and creature.light_on:
                creature.light()
        for block in Block.block_group:
            block = Block.block_group[block]
            if block.get_stat('light_source') > 0:
                block.light()

        # display
        self._camera.sync()
        self._camera.display(screen)
        self.player_info_display(player, screen)
        # reset buffer
        for particle in Particle.particle_group:
            particle = Particle.particle_group[particle]
            if isinstance(particle, DynamicStats):
                particle.reset()

    def player_info_display(self, player: Player, screen: pygame.Surface):
        health_bar_width = 300
        health_bar_height = 12
        resource_bar_length = 200
        stamina_bar_length = 150

        health_percent = player.health / player.max_health
        health_bar = pygame.Surface((health_percent * health_bar_width,
                                     health_bar_height))
        health_bar.fill((255, 0, 0))
        screen.blit(self.texts['health_bar'], (80, 60))
        screen.blit(health_bar, (80, 80))

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
            # print(clock.get_fps())
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
            pygame.display.flip()
        pygame.quit()


def compare_by_display_priority(p1: Particle, p2: Particle) -> bool:
    """ Sort by non-decreasing order """
    return p2.display_priority > p1.display_priority


def _load_assets():
    """ Load in game assets """
    path = "assets/images"
    paths = os.listdir(path)
    for p in paths:
        Particle.textures[p] = pygame.image.load(
            os.path.join(path, p)).convert_alpha()
        Particle.rotation[p] = {}
    path = "assets/sounds"
    paths = os.listdir(path)
    for p in paths:
        Particle.sounds[p] = pygame.mixer.Sound(os.path.join(path, p))

