from __future__ import annotations
import pygame
import math
from typing import List, Tuple, Union, Optional, Any, Set
from utilities import Positional, Displacable, Collidable, Lightable, Living, \
    Directional, get_direction, Staminaized
from settings import *
from error import InvalidConstructionInfo, UnknownTextureError
from data_structures import Queue


class Particle(Collidable, Directional):
    """
    Description: Customized sprites

    === Public Attributes ===
    - id: Identifier of the particle.
    - display_priority: The display priority of this particle, particles with
        the highest priority will be displayed on top of the screen

    - name: Name of this particle
    - map_display: Display in the map txt file
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
    sounds = {}
    game_map = {}  # dict[str, List[List[List[int]]]]
    tile_map = {}
    Scale = 1

    id: int
    display_priority: int
    texture: str
    map_display: str
    name: str
    occupation: dict[str, Set[Tuple[int, int]]]

    def __init__(self, info: dict[str, Union[str, float, int]]) -> None:
        default = {
            'display_priority': DEFAULT_DISPLAY_PRIORITY,
            'texture': DEFAULT_PARTICLE_TEXTURE,
            'name': Particle.ID + 1,
        }
        attr = ['display_priority', 'texture', 'name', 'map_display']
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

    def aim(self, obj: Positional) -> None:
        cx = self.x + self.diameter / 2 - 1
        cy = self.y + self.diameter / 2 - 1
        obj = (obj.x, obj.y)
        if isinstance(obj, Collidable):
            obj = (obj.x + obj.diameter / 2 - 1, obj.y + obj.diameter / 2 - 1)
        self.direction = get_direction((cx, cy), obj)

    def display(self, screen: pygame.Surface,
                location: Tuple[int, int]) -> None:
        radius = self.diameter / 2 * Particle.Scale
        texture = self.get_texture()
        centre_x = location[0] + radius - 1
        centre_y = location[1] + radius - 1
        size = texture.get_size()
        cx = centre_x - int(size[0] / 2) + 1
        cy = centre_y - int(size[1] / 2) + 1
        screen.blit(texture, [cx, cy])

    def get_texture(self):
        d = math.ceil(self.get_stat("diameter") * Particle.Scale)
        return get_texture_by_info(self.texture, (d, d), self.direction, 255)

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


class DisplacableParticle(Displacable, Particle):
    """ Particles that can change its position """

    def calculate_order(self) -> Tuple[float, float, int, int, int, int]:
        x_d = abs(self.get_stat('vx'))
        y_d = abs(self.get_stat('vy'))
        c_x = int(self.x)
        c_y = int(self.y)
        if self.get_stat('vx') == 0 and self.get_stat('vy') == 0:
            return 0, 0, 0, 0, 0, 0
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
                            current: int) \
            -> Tuple[float, float]:
        """ Change the position of the particle towards the given direction """
        vel = self.get_stat('v' + direction)

        for i in range(time):
            if total > 0:
                if total >= 1:
                    value = vel / abs(vel)
                    total -= 1
                else:
                    value = vel - int(vel)
                    total = 0
                setattr(self, direction, getattr(self, direction) + value)
                self.update_map_position()
                n = int(getattr(self, direction))
                if abs(n - current) >= 1:
                    particles = get_particles_by_tiles(
                        self.map_name,
                        colliding_tiles_generator(self.x, self.y,
                                                  self.diameter))
                    for particle in particles:
                        particle = Particle.particle_group[particle]
                        if not particle.id == self.id and particle.solid and \
                                self.solid \
                                and self.detect_collision(particle):
                            setattr(self, direction, getattr(self, direction) -
                                    value)
                            self.update_map_position()
                            setattr(self, "v" + direction, 0)
                            return 0, current
        return total, current

    def update_status(self):
        if not (self.get_stat("vx") == 0 and self.get_stat("vy") == 0):
            x_d, y_d, c_x, c_y, x_time, y_time = self.calculate_order()
            while x_d > 0 or y_d > 0:
                x_d, c_x = self.direction_increment(x_time, "x",
                                                    x_d, c_x)
                y_d, c_y = self.direction_increment(y_time, "y",
                                                    y_d, c_y)
        super().update_status()


class Block(Lightable, Particle):
    """

    """
    block_group = {}

    def __init__(self, info: dict[str, Union[str, float, int]]) -> None:
        super().__init__(info)
        Block.block_group[self.id] = self

    def remove(self):
        Particle.remove(self)
        Block.block_group.pop(self.id, None)

    def light(self) -> None:
        """ Raise brightness of nearby blocks """
        queue = Queue()
        called = set()
        called.add(self.id)
        value = self.get_stat("light_source") - self.get_stat("brightness")
        if value > 0:
            self.add_stats({"brightness": value})
        for block in get_particles_in_radius(self, 1, Block, False):
            if block.id not in called:
                queue.enqueue((self.id, block.id))
        while not queue.is_empty():
            item = queue.dequeue()
            p1 = Block.block_group[item[0]]
            p2 = Block.block_group[item[1]]
            value = p1.get_stat("brightness") - p1.get_stat('light_resistance')
            b2 = p2.get_stat("brightness")
            l2 = p2.get_stat("light_source")
            if value > 0 and value > b2 and value > l2:
                p2.add_stats({"brightness": value - b2})
                called.add(item[1])
                tiles = get_particles_in_radius(p2, 1, Block, False)
                for block in tiles:
                    if block.id not in called:
                        queue.enqueue((p2.id, block.id))


class ActiveParticle(Staminaized, Particle):
    """
    Description: Particles that can act on its own
    """
    ap_group = {}

    def __init__(self, info: dict[str, Union[str, float, int, Tuple]]) -> None:
        if "display_priority" not in info:
            info['display_priority'] = 2
        super().__init__(info)
        ActiveParticle.ap_group[self.id] = self

    def action(self) -> None:
        """ AI of this creature, this method should
        be called on every active creature regularly
        """
        raise NotImplementedError

    def get_tiles_in_contact(self) -> List[Block]:
        for t in self.occupation[self.map_name]:
            tile = Particle.game_map[self.map_name][t[0]][t[1]]
            for ps in tile:
                if ps in Block.block_group:
                    yield Block.block_group[ps]

    def remove(self):
        Particle.remove(self)
        ActiveParticle.ap_group.pop(self.id, None)


class Creature(ActiveParticle, Living):
    """
    Description: Active particles that are considered alive

    Additional Attributes:
        light_on: Whether this creature is illuminating its surroundings
        active: Whether this creature is active
        color: Displayed color of this creature
    Representation Invariants:

    """
    creature_group = {}
    creature_textures = {}
    color: Tuple[int, int, int]
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
        d = math.ceil(self.get_stat("diameter") * Particle.Scale)
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
            radius = self.diameter // 2 * Particle.Scale
            size = surface.get_size()
            cx = int(size[0] / 2)
            cy = int(size[1] / 2)
            pygame.draw.circle(
                surface, self.color, (cx, cy), radius)

    def action(self) -> None:
        """ AI of this creature, this method should
        be called on every active creature regularly
        """
        raise NotImplementedError

    def die(self):
        self.remove()

    def remove(self):
        ActiveParticle.remove(self)
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


def colliding_tiles_generator(x: float, y: float,
                              diameter: int,) -> List[Tuple[int, int]]:
    """ Generate the coordinates of the colliding tiles with the given info """
    start_col = int(x // TILE_SIZE)
    start_row = int(y // TILE_SIZE)
    end_col = int((x + diameter - 1) // TILE_SIZE)
    end_row = int((y + diameter - 1) // TILE_SIZE)
    for x in range(start_col, end_col + 1):
        for y in range(start_row, end_row + 1):
            yield y, x


def get_particles_by_tiles(map_name: str,
                           coordinates: List[Tuple[int, int]]) -> Set[int]:
    """ Return particle ids inside tiles given by the coordinates """
    mp = Particle.game_map[map_name]
    ps = set()
    for coord in coordinates:
        ps.update(mp[coord[0]][coord[1]].copy())
    return ps


def get_particles_in_radius(particle: Particle, radius=1, tp=None, corner=True) -> \
        List[Particle]:
    """ Return particles in the given radius through Generator """
    row = int(particle.y // TILE_SIZE)
    col = int(particle.x // TILE_SIZE)
    start_row = row - radius
    end_row = row + radius
    start_col = col - radius
    end_col = col + radius

    width = len(Particle.game_map[particle.map_name])
    height = len(Particle.game_map[particle.map_name][0])
    if start_row < 0:
        start_row = 0
    if end_row >= height:
        end_row = height - 1
    if start_col < 0:
        start_col = 0
    if end_col >= width:
        end_col = width - 1
    yielded = set()
    for x in range(start_row, end_row + 1):
        dif = abs(x - row)
        for y in range(start_col, end_col + 1):
            if not corner and abs(y - col) > (radius - dif):
                continue
            if tp == Block:
                yield Block.block_group[Particle.tile_map[particle.map_name][x][
                    y]]
            else:
                ps = Particle.game_map[particle.map_name][x][y]
                for p in ps.copy():
                    item = Particle.particle_group[p]
                    if item.id not in yielded:
                        if tp is not None:
                            if not isinstance(item, tp):
                                continue
                        yielded.add(item.id)
                        yield item


def get_nearby_particles(particle: Particle) -> Set[int]:
    """ Return a set of nearby particles around the given particle """
    r = set()
    tiles = colliding_tiles_generator(particle.x, particle.y, particle.diameter)
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
