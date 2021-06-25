import math

import pygame
from effect import *
from typing import Tuple, Union, List
from particles import Particle, Block, Creature, Player, Item
from positional import Movable
from bool_expr import BoolExpr
from predefined_particle import PredefinedParticle
from settings import *
import os


class GameMap:
    """
    Description: Game map object

    === Public Attributes ===
    name: name of the map
    tile_size: the size of each tile in pixels
    length: length of the map (in tiles)
    width: width of the map (in tiles)
    content: content of the map
    """
    name: str
    tile_size: int
    length: int
    width: int
    blocks: List[List[Block]]
    creatures: List[List[List[Creature]]]
    items: List[List[List[Item]]]

    def __init__(self, locations: dict[str, str],
                 look_up: dict[str, PredefinedParticle]) -> None:
        self.tile_size = TILE_SIZE
        content = ['blocks', 'creatures', 'items']
        for key in content:
            with open(locations[key], 'r') as file:
                lines = file.readlines()
                if key == 'blocks':
                    info = lines[0].split("_")
                    self.name = info[0]
                    self.length = int(info[1])
                    self.width = int(info[2])
                    self.blocks = []
                    rows = lines[1:]
                    for i in range(len(rows)):
                        row = rows[i]
                        self.blocks.append([])
                        for col in row:
                            pre_p = look_up[col]
                            particle_class = globals()[pre_p.info['class']]
                            self.blocks[i].append(particle_class(look_up))
                else:
                    result = []
                    for i in range(len(lines)):
                        line = lines[i]
                        result.append([])
                        for j in range(len(line)):
                            item = line[j]
                            result[i].append([])
                            pre_p = look_up[item]
                            particle_class = globals()[pre_p.info['class']]
                            result[i][j].append(particle_class(look_up))
                            setattr(self, key, result)


class Camera(Movable):
    """
    Camera used to display player/particle movements

    === Public Attributes ===
    - game_maps: game maps this camera operates on
    - screen: the screen to be displayed on
    - size: size of the camera in pixels
    - particle: the particle to be focused on
    - max_x: max x-coordinate of the camera on the current map
    - max_y: max y-coordinate of the camera on the current map
    - min_x: minimum y-coordinate of the camera on the current map
    - min_y: minimum y-coordinate of the camera on the current map
    """
    game_maps: dict[str, GameMap]
    screen: pygame.Surface
    width: int
    length: int
    particle: Particle
    max_x: int
    max_y: int
    min_x: int
    min_y: int

    def __init__(self, pos: dict[str, float], screen: pygame.Surface,
                 size: Tuple[int, int],
                 game_maps: List[GameMap]) -> None:
        Movable.__init__(self, pos)
        self.game_maps = {}
        for m in game_maps:
            self.game_maps[m.name] = m
        self.screen = screen
        self.length = size[0]
        self.width = size[1]
        self.min_x = 0
        self.min_y = 0
        current_map = self.game_maps[self.map_name]
        tile_size = current_map.tile_size
        self.max_x = current_map.length * tile_size - self.length
        self.max_y = current_map.width * tile_size - self.width

    def sync(self):
        """
        Synchronize the position of this camera with the particle
        """
        self.map_name = self.particle.map_name
        current_map = self.game_maps[self.map_name]
        tile_size = current_map.tile_size
        self.max_x = current_map.length * tile_size - self.length
        self.max_y = current_map.width * tile_size - self.width

    def display(self):
        """ Display the content onto the screen
        """
        current_map = self.game_maps[self.map_name]
        start_col = self.x // TILE_SIZE
        start_row = self.y // TILE_SIZE
        end_col = math.ceil(self.x / TILE_SIZE) + self.length
        end_row = math.ceil(self.y / TILE_SIZE) + self.width
        for i in range(start_row, end_row):
            for j in range(start_col, end_col):
                tile = current_map.content['block'][i][j]
                display_x = tile.x - self.x
                display_y = tile.y - self.y
                tile.display(
                    self.screen, (display_x, display_y))

    def adjust_position(self):
        """
        Adjust the position of the camera if it reaches the boarder of the map
        """
        self.x = self.particle.x
        self.y = self.particle.y
        if self.x > self.max_x:
            self.x = self.max_x
        if self.x < self.min_x:
            self.x = self.min_x
        if self.y > self.max_y:
            self.y = self.max_y
        if self.y < self.min_y:
            self.y = self.min_y


class Level:
    """
    Description: Levels of the game

    === Public Attributes ===
    difficulty: difficulty of the level
    goal: The goal of the level

    === Private Attributes ===
    _asset: Loaded assets of the game
    _asset_name: The locations of game assets
    _game_maps: Loaded game maps, accessed by their names
    _camera: Camera for this level
    _initialized: Whether the level has been initialized

    === Representation Invariants ===
    - difficulty must be an integer from 0 - 3
    """
    difficulty: int
    goal: BoolExpr
    _game_maps: dict[str, GameMap]
    _camera: Camera
    _asset: dict[str, dict[str, Union[pygame.Surface, pygame.mixer.Sound, str]]]
    _asset_location: List[str]
    _initialized: bool

    def __init__(self, asset: List[str]) -> None:
        self._asset_name = asset
        self.difficulty = 0  # default difficulty
        self._initialized = False

    def _load_assets(self) -> None:
        sound_format = ['wav']
        image_format = ['png', 'jpg', 'gif', 'bmp', 'tif']
        music_format = ['mp3', 'mp4']
        map_format = ['txt']

        # load in predefined particles
        look_up = {}
        with open('predefined-particles.txt', 'r') as file:
            for line in file:
                p = PredefinedParticle(line)
                look_up[p.info['name']] = p

        for location in self._asset_name:
            data = location.split('.')
            suffix = data[1]
            # data[0]: name of the file without suffix
            if suffix in sound_format:
                self._asset['sound'][data[0]] = pygame.mixer.Sound(location)
            elif suffix in image_format:
                self._asset['image'][data[0]] = pygame.image.load(location)
            elif suffix in music_format:
                self._asset['music'][data[0]] = data[1]
            elif suffix in map_format:
                m = GameMap(location, look_up)

    def run(self, screen: pygame.Surface, difficulty=0):
        """
        Run the level with the given setting
        """
        if not self._initialized:
            self._load_assets()
            self._initialized = True
            self.difficulty = difficulty

    def exit(self):
        """
        Release memory of loaded resources and exit the level
        """
        self.difficulty = 0  # reset difficulty
        del self._asset


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
    """
    _screen: pygame.Surface
    _levels: List[Level]
    _frame_rate: int
    _level_selecting: bool
    _level_running: bool

    def start(self) -> None:
        """
        Initialize the engine and start the game.
        """
        self._level_selecting = True
        self._level_running = False
        pygame.init()
        pygame.mixer.init()
        self._apply_settings()
        self._load_level()
        self.run()

    def _apply_settings(self) -> None:
        """
        Apply game gui settings
        """
        pygame.display.set_icon(ICON)
        self._screen = pygame.display.set_mode(SCREEN_SIZE)
        pygame.display.set_caption(CAPTION)
        self.frame_rate = FPS

    def _load_level(self) -> None:
        """
        Load levels from the "Levels" folder into the game.
        """
        levels = os.listdir("Levels")
        for lev in levels:
            with open(lev, 'r+') as level_file:
                self._levels.append(Level(level_file.readlines()))

    def run(self) -> None:
        clock = pygame.time.Clock()
        running = True
        while running:
            clock.tick(self.frame_rate)
            if self._level_selecting:
                pass
            elif self._level_running:
                pass
            pygame.display.flip()
        return
