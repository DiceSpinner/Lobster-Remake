import math

import pygame
from effect import *
from typing import Tuple, Union, List, TypeVar, Optional
from particles import Particle, Block, Creature, Item, Player
from utilities import Positional, Movable, Collidable
from bool_expr import BoolExpr
from predefined_particle import PredefinedParticle
from settings import *
from data_structures import PriorityQueue
from math_formula import segment_intersection, line_circle_intersection
import os


class GameMap:
    """
    Description: Game map object

    === Public Attributes ===
    name: name of the map
    tile_size: the size of each tile in pixels
    length: length of the map (in tiles)
    width: width of the map (in tiles)
    blocks: blocks of the map
    entities: creatures and items inside the map
    """
    name: str
    tile_size: int
    length: int
    width: int
    blocks: List[List[Block]]
    entities: List[List[List[Union[Creature, Item]]]]

    def __init__(self, location: str,
                 look_up: dict[str, PredefinedParticle]) -> None:
        self.tile_size = TILE_SIZE
        with open(location, 'r') as file:
            lines = file.readlines()
            info = lines[0].split(" ")
            self.name = info[0]
            self.length = int(info[1])
            self.width = int(info[2])

            rows = lines[1:]
            self.blocks = []
            self.entities = []
            for i in range(len(rows)):
                pos_y = i * TILE_SIZE
                row = rows[i].rstrip()
                self.blocks.append([])
                self.entities.append([])
                row = row.split("	")
                for j in range(len(row)):
                    pos_x = j * TILE_SIZE
                    self.entities[i].append([])
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
                        else:
                            self.entities[i][j].append(par)

    def update_content(self):
        """ Update the location of entities """
        for i in range(len(self.entities)):
            row = self.entities[i]
            for j in range(len(row)):
                col = row[j]
                for k in range(len(col)):
                    entity = col[k]
                    if isinstance(entity, Movable):
                        entity.update_position()
                        self.entity_collision_check([i, j, k])
                        self.entities[i][j].remove(entity)
                        self.entities[int(entity.y // TILE_SIZE)][
                            int(entity.x // TILE_SIZE)].append(entity)

    def entity_collision_check(self, index: List[int]) -> None:
        row = index[0]
        col = index[1]
        k = index[2]
        start_row = row - 1
        start_col = col - 1
        end_row = row + 1
        end_col = col + 1
        entity = self.entities[row][col][k]
        if start_row < 0:
            start_row = 0
        if start_col < 0:
            start_col = 0
        if end_row >= len(self.entities):
            end_row = len(self.entities) - 1
        if end_col >= len(self.entities[end_row]):
            end_col = len(self.entities[end_row]) - 1
        for i in range(start_row, end_row + 1):
            for j in range(start_col, end_col + 1):
                tile = self.blocks[i][j]
                if entity.detect_collision(tile):
                    # print('Collide with row:' + str(i), "col:" + str(j))
                    if isinstance(entity, Movable) and (not entity.vx == 0 or
                                                        not entity.vy == 0):
                        correct_position(entity, tile)


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
    length: int
    width: int
    particle: Particle
    max_x: int
    max_y: int
    min_x: int
    min_y: int

    def __init__(self, particle: Particle,
                 length: int, width: int,
                 game_maps: dict[str, GameMap]) -> None:
        Positional.__init__(self, {"map_name": particle.map_name})
        self.particle = particle
        self.game_maps = game_maps
        self.width = width
        self.length = length
        self.min_x = 0
        self.min_y = 0
        self.sync()

    def sync(self):
        """
        Synchronize the position of this camera with the particle
        """
        self.map_name = self.particle.map_name
        self.x = self.particle.x - self.length / 2
        self.y = self.particle.y - self.width / 2
        current_map = self.game_maps[self.map_name]
        tile_size = current_map.tile_size
        self.max_x = current_map.length * tile_size - self.length
        self.max_y = current_map.width * tile_size - self.width
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
        end_row = int(math.ceil((self.x + self.length) / TILE_SIZE))
        start_col = int(self.y // TILE_SIZE)
        end_col = int(math.ceil((self.y + self.width) / TILE_SIZE))
        for i in range(start_row, end_row):
            for j in range(start_col, end_col):
                tile = current_map.blocks[j][i]
                items = [tile] + current_map.entities[j][i]
                for item in items:
                    display_x = round(item.x - self.x)
                    display_y = round(item.y - self.y)
                    displaying[item.id] = (display_x, display_y)
        queue = PriorityQueue(compare_by_display_priority)
        for key in displaying:
            queue.enqueue(Particle.particle_group[key])
        while not queue.is_empty():
            item = queue.dequeue()
            item.display(screen, displaying[item.id])


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

    def __init__(self, asset: List[str]) -> None:
        for line in asset:
            line = line.split('=')
            if line[0] == 'maps':
                self._map_names = line[1].split(':')
        self.difficulty = 0  # default difficulty
        self._initialized = False
        self._game_maps = {}
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

    def run(self, screen: pygame.Surface, difficulty=0):
        """
        Run the level with the given setting
        """
        if not self._initialized:
            self._load_maps()
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
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYUP or event.type == pygame.KEYDOWN:
                player_input.append(event)
        for creature in Creature.creature_group:
            Creature.creature_group[creature].action(player_input)

        for game_map in self._game_maps:
            game_map = self._game_maps[game_map]
            game_map.update_content()

        self._camera.sync()
        self._camera.display(screen)

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
            pygame.display.flip()
        pygame.quit()


def compare_by_display_priority(p1: Particle, p2: Particle) -> bool:
    """ Sort by non-decreasing order """
    return p2.display_priority > p1.display_priority


def correct_position(c1: Collidable, c2: Collidable) -> None:
    """ Correct the position of c1 so it doesn't collide with c2 "

    Pre-condition: c1 implements the Movable interface
    """
    if c1.shape == SQUARE and c2.shape == SQUARE:
        _square_square(c1, c2)
        return
    if c1.shape == CIRCLE and c2.shape == SQUARE:
        _circle_square(c1, c2)
        return
    if c1.shape == SQUARE and c2.shape == CIRCLE:
        pass


def _square_square(c1: Collidable, c2: Collidable) -> None:
    corner_upleft = (c1.x, c1.y)
    corner_upright = (c1.x + c1.diameter, c1.y)
    corner_bottomleft = (c1.x, c1.y + c1.diameter)
    corner_bottomright = (c1.x + c1.diameter, c1.y + c1.diameter)

    corners = [corner_upleft, corner_upright, corner_bottomleft,
               corner_bottomright]
    collided = []

    for corner in corners:
        if c2.x <= corner[0] <= c2.x + c2.diameter and c2.y <= corner[
             1] <= c2.y + c2.diameter:
            collided.append(corner)
    left = ((c2.x - 1, c2.y - 1), (c2.x - 1, c2.y + c2.diameter + 1))
    up = ((c2.x - 1, c2.y - 1), (c2.x + 1 + c2.diameter, c2.y - 1))
    right = ((c2.x + 1 + c2.diameter, c2.y - 1), (c2.x + c2.diameter + 1,
                                                  c2.y + c2.diameter + 1))
    down = ((c2.x - 1, c2.y + c2.diameter + 1), (c2.x + 1 + c2.diameter,
                                                 c2.y + c2.diameter + 1))
    sides = [left, up, right, down]
    previous = []
    for i in range(len(collided)):
        corner = collided[i]
        previous.append((corner[0] - c1.vx, corner[1] - c1.vy))
    for i in range(len(collided)):
        corner = collided[i]
        for side in sides:
            poi = segment_intersection(side, (corner, previous[i]))
            if poi is not None:
                x = poi[0] - corner[0]
                y = poi[1] - corner[1]
                c1.x += x
                c1.y += y
                for c in range(len(collided)):
                    co = collided[c]
                    collided[c] = (co[0] + x, co[1] + y)


def _circle_square(c1: Collidable, c2: Collidable) -> None:
    centre_x = c1.x + c1.diameter / 2
    centre_y = c1.y + c1.diameter / 2
    tl = (c2.x - 1, c2.y - 1)
    tr = (c2.x + c2.diameter + 1, c2.y - 1)
    br = (c2.x + c2.diameter + 1, c2.y + c2.diameter + 1)
    bl = (c2.x - 1, c2.y + c2.diameter + 1)
    p1 = None
    p2 = None
    if centre_x <= tl[0] and centre_y <= tl[1]:
        p1 = tl
        p2 = (p1[0] - c1.vx, p1[1] - c1.vy)
    elif centre_x >= tr[0] and centre_y <= tr[1]:
        p1 = tr
        p2 = (p1[0] - c1.vx, p1[1] - c1.vy)
    elif centre_x >= br[0] and centre_y >= br[1]:
        p1 = br
        p2 = (p1[0] - c1.vx, p1[1] - c1.vy)
    elif centre_x <= bl[0] and centre_y >= bl[1]:
        p1 = bl
        p2 = (p1[0] - c1.vx, p1[1] - c1.vy)
    if p1 is not None and p2 is not None:
        poi = line_circle_intersection((p1, p2), (c1.x, c1.y), c1.diameter)
        print(poi)
        for point in poi:
            if c2.x <= point[0] <= c2.x + c2.diameter and \
                    c2.y <= point[1] <= c2.y + c2.diameter:
                offset_x = p1[0] - point[0]
                offset_y = p1[1] - point[1]
                c1.x += offset_x
                c1.y += offset_y
    else:
        _square_square(c1, c2)


def _circle_circle(c1: Collidable, c2: Collidable) -> None:
    pass
