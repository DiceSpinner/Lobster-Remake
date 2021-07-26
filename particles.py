from __future__ import annotations
import pygame
from typing import List, Tuple, Union, Optional, Any, Set
from utilities import Positional, Movable, Collidable, Lightable, Living, \
    Directional, get_direction
from bool_expr import BoolExpr, construct_from_str
from settings import *
from error import InvalidConstructionInfo


class Particle(Collidable):
    """
    Description: Customized sprites

    === Public Attributes ===
    - id: Identifier of the particle.
    - display_priority: The display priority of this particle, particles with
        the highest priority will be displayed on top of the screen

    - name: Name of this particle (displayed in map txt file)

    === Private Attributes ===
    -
    """
    # static fields
    ID = 0
    particle_group = {}
    new_particles = {}
    light_particles = {}
    textures = {}
    rotation = {}
    sounds = {}
    game_map = {}  # dict[str, List[List[List[int]]]]

    id: int
    display_priority: int
    texture: str
    _texture: pygame.Surface
    name: str
    occupation: dict[str, Set[Tuple[int, int]]]

    def __init__(self, info: dict[str, Union[str, float, int]]) -> None:
        default = {
            'display_priority': DEFAULT_DISPLAY_PRIORITY,
            'texture': DEFAULT_PARTICLE_TEXTURE,
            'name': DEFAULT_PARTICLE_NAME,
        }
        attr = ['display_priority', 'texture', 'name']
        super().__init__(info)
        self.id = Particle.ID
        Particle.ID += 1
        for key in default:
            if key not in info:
                info[key] = default[key]
        for item in info:
            if item in attr:
                setattr(self, item, info[item])
        self.occupation = {self.map_name: set()}
        self._texture = pygame.transform.scale(Particle.textures[self.texture],
                                               (self.diameter, self.diameter))
        Particle.particle_group[self.id] = self
        Particle.new_particles[self.id] = self

    def display(self, screen: pygame.Surface,
                location: Tuple[int, int]) -> None:
        screen.blit(self._texture, location)

    def remove(self):
        """ Remove this particle from the game """
        Particle.particle_group.pop(self.id, None)
        for coor in self.occupation[self.map_name]:
            Particle.game_map[self.map_name][coor[0]][coor[1]].remove(self.id)

    def update_map_position(self):
        """ Update the position of the particle on the game map """
        occupied = self.occupation.copy()
        new_pos = calculate_colliding_tiles(self.x, self.y,
                                            self.get_stat('diameter'))
        for mp in occupied:
            for point in occupied[mp].copy():
                if not mp == self.map_name or point not in new_pos:
                    self.occupation[mp].remove(point)
                    Particle.game_map[mp][point[0]][point[1]].remove(self.id)
                else:
                    new_pos.remove(point)
        for point in new_pos:
            if self.map_name not in self.occupation:
                self.occupation[self.map_name] = set()
            self.occupation[self.map_name].add(point)
            Particle.game_map[self.map_name][point[0]][point[1]].add(self.id)

    def __str__(self):
        return self.name


class DirectionalParticle(Particle, Directional):
    """ Collidable particles that implements the directional interface """

    def __init__(self, info: dict[str, Union[str, float, int, Tuple]]) -> None:
        super().__init__(info)
        if self.texture not in Particle.rotation:
            Particle.rotation[self.texture] = {self.diameter: {}}
        else:
            Particle.rotation[self.texture][self.diameter] = {}

    def aim(self, obj: Positional) -> None:
        cx = self.x + self.diameter / 2 - 1
        cy = self.y + self.diameter / 2 - 1
        obj = (obj.x, obj.y)
        if isinstance(obj, Collidable):
            obj = (obj.x + obj.diameter / 2 - 1, obj.y + obj.diameter / 2 - 1)
        self.direction = get_direction((cx, cy), obj)

    def display(self, screen: pygame.Surface,
                location: Tuple[int, int]) -> None:
        radius = self.diameter / 2
        texture = self.get_texture()
        centre_x = location[0] + radius - 1
        centre_y = location[1] + radius - 1
        size = texture.get_size()
        cx = centre_x - round(size[0] / 2, 0) + 1
        cy = centre_y - round(size[1] / 2, 0) + 1
        screen.blit(texture, [cx, cy])

    def get_texture(self):
        """ Return the texture of current direction """
        if self.direction not in Particle.rotation[self.texture][self.diameter]:
            Particle.rotation[self.texture][self.diameter][self.direction] = \
                pygame.transform.rotate(self._texture, self.direction)
        return Particle.rotation[self.texture][self.diameter][self.direction]


class MovableParticle(DirectionalParticle, Movable):
    """ Directional particles that implements the movable interface
    """

    def __init__(self, info: dict[str, Union[str, float, int, Tuple]]) -> None:
        super().__init__(info)

    def calculate_order(self) -> Tuple[float, float, int, int, int, int]:
        x_d = abs(self.get_stat('vx'))
        y_d = abs(self.get_stat('vy'))
        c_x = int(self.x)
        c_y = int(self.y)
        if self.get_stat('vx') == 0 and self.get_stat('vy') == 0:
            return 0, 0, 0, 0, 0, 0
        if self.get_stat('vx') == 0 and self.get_stat('vy') == 0:
            return
        if self.get_stat('vx') == 0:
            x_time = 0
            y_time = 1
        elif self.get_stat('vy') == 0:
            x_time = 1
            y_time = 0
        elif abs(self.get_stat('vx')) > abs(self.get_stat('vy')):
            x_time = int(round(abs(self.get_stat('vx')) / abs(self.get_stat(
                'vy')), 0))
            y_time = 1
        elif abs(self.get_stat('vx')) < abs(self.get_stat('vy')):
            x_time = 1
            y_time = int(round(abs(self.get_stat('vy')) / abs(self.get_stat(
                'vx')), 0))
        else:
            x_time, y_time = 1, 1
        return x_d, y_d, c_x, c_y, x_time, y_time

    def direction_increment(self, time: int, direction: str, total: float,
                            current: int)\
            -> Tuple[float, float]:
        """ Increment the position of the particle in given direction """
        vel = 'v' + direction
        for i in range(time):
            if total > 0:
                if total >= 1:
                    value = self.get_stat(vel) / abs(self.get_stat(vel))
                    total -= 1
                else:
                    value = self.get_stat(vel) - int(self.get_stat(vel))
                    total = 0
                setattr(self, direction, getattr(self, direction) + value)
                n = int(getattr(self, direction))
                if abs(n - current) >= 1:
                    particles = get_particles_by_tiles(
                        self.map_name,
                        calculate_colliding_tiles(self.x, self.y,
                                                  self.diameter))
                    for particle in particles:
                        particle = Particle.particle_group[particle]
                        if not particle.id == self.id and particle.solid and \
                                self.solid \
                                and self.detect_collision(particle):
                            setattr(self, direction, getattr(self, direction) -
                                    value)
                            total = 0
                            break
        return total, current

    def update_position(self) -> None:
        x_d, y_d, c_x, c_y, x_time, y_time = self.calculate_order()
        while x_d > 0 or y_d > 0:
            x_d, c_x = self.direction_increment(x_time, "x",
                                                x_d, c_x)
            y_d, c_y = self.direction_increment(y_time, "y",
                                                y_d, c_y)
        self.update_map_position()


class Block(Particle, Lightable):
    """

    """
    block_group = {}

    def __init__(self, info: dict[str, Union[str, float, int]]) -> None:
        super().__init__(info)
        Block.block_group[self.id] = self

    def remove(self):
        Particle.remove(self)
        Block.block_group.pop(self.id, None)

    def get_tiles_in_radius(self, radius=1, corner=True) -> List[Block]:
        """ Return tiles in the given radius """
        row = int(self.y // TILE_SIZE)
        col = int(self.x // TILE_SIZE)
        start_row = row - radius
        end_row = row + radius
        start_col = col - radius
        end_col = col + radius

        width = len(Particle.game_map[self.map_name])
        height = len(Particle.game_map[self.map_name][0])
        if start_row < 0:
            start_row = 0
        if end_row >= height:
            end_row = height - 1
        if start_col < 0:
            start_col = 0
        if end_col >= width:
            end_col = width - 1

        tiles = []
        for x in range(start_row, end_row + 1):
            dif = abs(x - row)
            for y in range(start_col, end_col + 1):
                if not corner and abs(y - col) > (radius - dif):
                    continue
                ps = Particle.game_map[self.map_name][x][y]
                for p in ps:
                    if p in Block.block_group:
                        tiles.append(Block.block_group[p])
        return tiles

    def light(self):
        self.enlighten(self)
        if self.get_stat('brightness') > 0:
            blocks = self.get_tiles_in_radius(1, False)
            for block in blocks:
                if not block.id == self.id:
                    if block.get_stat('brightness') < self.get_stat(
                            'brightness'):
                        self.enlighten(block)
                        block.light()


class Creature(MovableParticle, Living, Lightable):
    """
    Description: Movable particles that can act on its own

    Additional Attributes:
        light_on: Whether this creature is illuminating its surroundings
        active: Whether this creature is active
        color: Displayed color of this creature
    Representation Invariants:

    """
    creature_group = {}
    active: bool
    color: Tuple[int, int, int]
    rotation: dict[int, dict[float, pygame.Surface]]
    light_on: bool

    def __init__(self, info: dict[str, Union[str, float, int, Tuple]]) -> None:
        if "display_priority" not in info:
            info['display_priority'] = 2
        super().__init__(info)
        if 'color' in info:
            self._texture = pygame.transform.scale(
                Particle.textures[self.texture], (self.diameter * 2,
                                                  self.diameter * 2))
        Creature.creature_group[self.id] = self
        attr = ["active", 'color', 'light_on']
        default = {
            'active': True,
            'color': None,
            'light_on': True
        }
        for key in default:
            if key not in info:
                info[key] = default[key]
        for item in info:
            if item in attr:
                setattr(self, item, info[item])

    def get_texture(self):
        if self.id in Creature.rotation:
            if self.direction in Creature.rotation[self.id]:
                surface = Creature.rotation[self.id][self.direction]
            else:
                surface = DirectionalParticle.get_texture(self)
                self._draw_color_on_texture(surface)
                Creature.rotation[self.id][self.direction] = surface
        else:
            surface = DirectionalParticle.get_texture(self)
            self._draw_color_on_texture(surface)
            Creature.rotation[self.id] = {self.direction: surface}
        return surface

    def _draw_color_on_texture(self, surface: pygame.Surface) -> None:
        if self.color is not None:
            radius = self.diameter // 2
            size = surface.get_size()
            cx = round(size[0] / 2, 0)
            cy = round(size[1] / 2, 0)
            pygame.draw.circle(
                surface, self.color, (cx, cy), radius)

    def action(self, player_input: Optional[List[pygame.event.Event]]) -> None:
        """ AI of this creature, this method should
        be called on every active creature regularly
        """
        raise NotImplementedError

    def get_tiles_in_contact(self) -> List[Block]:
        bs = []
        for t in self.occupation[self.map_name]:
            tile = Particle.game_map[self.map_name][t[0]][t[1]]
            for ps in tile:
                if ps in Block.block_group:
                    bs.append(Block.block_group[ps])
        return bs

    def light(self):
        tiles = self.get_tiles_in_contact()
        sl = self.get_stat('light_source')
        for tile in tiles:
            ol = tile.get_stat('light_source')
            if ol < sl:
                tile.add_stats({'light_source': sl - ol})

    def die(self):
        self.remove()

    def remove(self):
        Particle.remove(self)
        Creature.creature_group.pop(self.id, None)


def calculate_colliding_tiles(x: float, y: float, diameter: int,
                              ) -> List[Tuple[int, int]]:
    """ Return the coordinates of the colliding tiles with the given info """
    start_col = int(x // TILE_SIZE)
    start_row = int(y // TILE_SIZE)
    end_col = int((x + diameter - 1) // TILE_SIZE)
    end_row = int((y + diameter - 1) // TILE_SIZE)
    new_pos = []
    for x in range(start_col, end_col + 1):
        for y in range(start_row, end_row + 1):
            new_pos.append((y, x))
    return new_pos


def get_particles_by_tiles(map_name: str,
                           coordinates: List[Tuple[int, int]]) -> Set[int]:
    """ Return particle ids inside tiles given by the coordinates """
    mp = Particle.game_map[map_name]
    ps = set()
    for coord in coordinates:
        ps.update(mp[coord[0]][coord[1]].copy())
    return ps


def get_nearby_particles(particle: Particle) -> Set[int]:
    """ Return a set of nearby particles around the given particle """
    r = set()
    tiles = calculate_colliding_tiles(particle.x, particle.y, particle.diameter)
    r.update(get_particles_by_tiles(particle.map_name, tiles))
    return r
