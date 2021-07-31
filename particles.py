from __future__ import annotations
import pygame
import math
from typing import List, Tuple, Union, Optional, Any, Set
from utilities import Positional, Movable, Collidable, Lightable, Living, \
    Directional, get_direction, Staminaized
from bool_expr import BoolExpr, construct_from_str
from settings import *
from error import InvalidConstructionInfo, UnknownTextureError
from data_structures import Queue


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
    raw_textures = {}
    textures = {}
    rotation = {}
    sounds = {}
    game_map = {}  # dict[str, List[List[List[int]]]]

    id: int
    display_priority: int
    texture: str
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
        self.update_map_position()
        Particle.particle_group[self.id] = self
        Particle.new_particles[self.id] = self

    def display(self, screen: pygame.Surface,
                location: Tuple[int, int]) -> None:
        d = self.get_stat("diameter")
        texture = get_texture_by_info(self.texture, (d, d), 0, 255)
        screen.blit(texture, location)

    def remove(self):
        """ Remove this particle from the game """
        Particle.particle_group.pop(self.id, None)
        for coor in self.occupation[self.map_name]:
            Particle.game_map[self.map_name][coor[0]][coor[1]].remove(self.id)

    def update_map_position(self):
        """ Update the position of the particle on the game map """
        occupied = self.occupation.copy()
        new_pos = calculate_colliding_tiles(round(self.x, 0), round(self.y, 0),
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
        d = self.get_stat("diameter")
        return get_texture_by_info(self.texture, (d, d), self.direction, 255)


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

    def light(self) -> None:
        """ Raise brightness of nearby blocks """
        queue = Queue()
        called = set()
        called.add(self.id)
        self.enlighten(self)
        for block in self.get_tiles_in_radius(1, False):
            if block.id not in called:
                queue.enqueue((self.id, block.id))
        while not queue.is_empty():
            item = queue.dequeue()
            p1 = Block.block_group[item[0]]
            p2 = Block.block_group[item[1]]
            value = p1.get_stat("brightness") - p1.get_stat('light_resistance')
            if not (value < p2.get_stat("brightness") or value < p2.get_stat(
                    "light_source")):
                p1.enlighten(p2)
                called.add(item[1])
                tiles = p2.get_tiles_in_radius(1, False)
                if p2.get_stat("brightness") > 0:
                    for block in tiles:
                        if block.id not in called:
                            queue.enqueue((p2.id, block.id))


class Creature(DirectionalParticle, Living, Lightable):
    """
    Description: Movable particles that can act on its own

    Additional Attributes:
        light_on: Whether this creature is illuminating its surroundings
        active: Whether this creature is active
        color: Displayed color of this creature
    Representation Invariants:

    """
    creature_group = {}
    creature_textures = {}
    active: bool
    color: Tuple[int, int, int]
    rotation: dict[int, dict[float, pygame.Surface]]
    light_on: bool

    def __init__(self, info: dict[str, Union[str, float, int, Tuple]]) -> None:
        if "display_priority" not in info:
            info['display_priority'] = 2
        super().__init__(info)
        Creature.creature_group[self.id] = self
        attr = ["active", 'color', 'light_on']
        default = {
            'active': True,
            'color': (255, 255, 255),
            'light_on': True
        }
        for key in default:
            if key not in info:
                info[key] = default[key]
        for item in info:
            if item in attr:
                setattr(self, item, info[item])

    def get_texture(self):
        d = self.get_stat("diameter")
        tup = (self.texture, (d, d), self.direction, 255, self.color)
        try:
            return Creature.creature_textures[tup].copy()
        except KeyError:
            raw = get_texture_by_info(self.texture, (d * 2, d * 2),
                                      self.direction, 255)
            self._draw_color_on_texture(raw)
            Creature.creature_textures[tup] = raw
            return raw.copy()

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


def get_texture_by_info(name: str, size: Tuple[int, int], direction: float,
                        alpha: int) \
        -> pygame.Surface:
    """ Return the texture with the given info, if texture with the given
    configuration does not exist but is loaded into Particle.raw_textures,
    generate the texture with this configuration and return it.
    """
    if name in Particle.raw_textures:
        tup = (name, size, direction, alpha)
        try:
            return Particle.textures[tup].copy()
        except KeyError:
            raw_texture = Particle.raw_textures[name]
            scaled = pygame.transform.scale(raw_texture, size)
            rotated = pygame.transform.rotate(scaled, direction)
            rotated.set_alpha(alpha)
            Particle.textures[tup] = rotated
            return rotated.copy()
    raise UnknownTextureError
