from __future__ import annotations
import pygame
import math
import public_namespace
from typing import List, Tuple, Union, Set, Any
from utilities import Positional, Displacable, Collidable, Lightable, Living, \
    Directional, get_direction, Staminaized, Interactive, Animated, UpdateReq
from settings import *
from data_structures import Queue
from item import *


class Particle(Collidable, Directional):
    """
    Description: Customized sprites

    === Public Attributes ===
    - id: Identifier of the particle.
    - display_priority: The display priority of this particle, particles with
        the highest priority will be displayed on top of the screen

    - name: Name of this particle
    - map_display: Display in the map txt file
    - texture: The texture of this particle

    === Private Attributes ===

    """
    # static fields
    ID = 0
    particle_group = {}
    new_particles = {}
    light_particles = {}
    textures = {}

    id: int
    display_priority: int
    texture: str
    map_display: str
    name: str
    _occupation: dict[str, Set[Tuple[int, int]]]

    def __init__(self, info: dict[str, Union[str, float, int]]) -> None:
        default = {
            'display_priority': DEFAULT_DISPLAY_PRIORITY,
            'texture': DEFAULT_PARTICLE_TEXTURE,
            'name': Particle.ID + 1,
            'map_display': DEFAULT_PARTICLE_DISPLAY
        }
        attr = ['display_priority', 'texture', 'name', 'map_display']
        super().__init__(info)
        self.id = Particle.ID
        Particle.ID += 1
        for key in default:
            if key not in info:
                info[key] = default[key]
        for item in attr:
            setattr(self, item, info[item])
        self._occupation = {self.map_name: set()}
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
        radius = self.diameter / 2 * public_namespace.scale
        texture = self.get_texture()
        centre_x = location[0] + radius - 1
        centre_y = location[1] + radius - 1
        size = texture.get_size()
        cx = centre_x - int(size[0] / 2) + 1
        cy = centre_y - int(size[1] / 2) + 1
        screen.blit(texture, [cx, cy])

    def get_texture(self):
        d = math.ceil(self.get_stat("diameter") * public_namespace.scale)
        return public_namespace.get_texture_by_info(self.texture, (d, d),
                                                    self.direction, 255)

    def remove(self):
        """ Remove this particle from the game """
        Particle.particle_group.pop(self.id, None)
        for cod in self._occupation[self.map_name]:
            public_namespace.game_map[self.map_name][cod[0]][cod[1]].remove(
                self.id)

    def update_map_position(self):
        """ Update the position of the particle on the game map """
        occupied = self._occupation.copy()
        new_pos = calculate_colliding_tiles(int(self.x), int(self.y),
                                            self.get_stat('diameter'))
        for mp in occupied:
            for point in occupied[mp].copy():
                if not mp == self.map_name or point not in new_pos:
                    self._occupation[mp].remove(point)
                    public_namespace.game_map[mp][point[0]][point[1]].remove(
                        self.id)
                else:
                    new_pos.remove(point)
        for point in new_pos:
            if self.map_name not in self._occupation:
                self._occupation[self.map_name] = set()
            self._occupation[self.map_name].add(point)
            public_namespace.game_map[self.map_name][point[0]][point[1]].add(
                self.id)

    def get_tiles_in_contact(self) -> List[Block]:
        for t in self._occupation[self.map_name]:
            tile = public_namespace.tile_map[self.map_name][t[0]][t[1]]
            yield Particle.particle_group[tile]

    def __str__(self):
        return self.name


class AnimatedParticle(Animated, Particle):
    """ Animated particles

    === Public Attributes ===
    - animation: A list of images represents the animation for this particle

    === Private Attributes ===
    - _display_counter: Counter for the animation display of the particle
    """
    animation: List[str]
    _display_counter: int

    def __init__(self, info: dict[str, Any]) -> None:
        default = {
            'animation': [DEFAULT_PARTICLE_TEXTURE]
        }
        attr = ['animation']
        for key in default:
            if key not in info:
                info[key] = default[key]
        for item in attr:
            setattr(self, item, info[item])
        super().__init__(info)
        assert len(self.animation) > 0
        self._display_counter = 0

    def update_status(self):
        self._display_counter += 1
        if self._display_counter >= len(self.animation):
            self._display_counter = 0
        self.texture = self.animation[self._display_counter]
        super().update_status()


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


class Storage(Particle):
    """ Particles with inventory

    """
    inventory: Inventory

    def __init__(self, info: dict[str, Any]) -> None:
        self.inventory = info['inventory']
        super().__init__(info)


class LootItem(Interactive, UpdateReq, Particle):
    """ A particle wrapper class for items

    === Public Attribute ===
    - item: The item this particle contains

    """
    item: Item

    def __init__(self, info: dict[str, Any]) -> None:
        self.item = info['item']
        info['texture'] = self.item.image
        info['display_priority'] = ITEM_DISPLAY_PRIORITY
        info['diameter'] = self.item.diameter
        info['shape'] = self.item.shape
        info['update_frequency'] = None
        super().__init__(info)

    def upon_interact(self, other: Any) -> None:
        assert isinstance(other, Storage)
        other.inventory.add(self.item)
        UpdateReq.update_queue.enqueue(self)

    def update_status(self):
        if self.item.stack == 0:
            self.remove()

    def can_interact(self, other: Any) -> bool:
        return isinstance(other, Storage) and other.detect_collision(self)


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

    === Public Attributes ===
    - interact_range: The range this particle can interact with other
        interactive particles

    === Private Attributes ===
    - _interactive_particles: A set of particles that this particle can
        interact with, this field must be updated every frame
    """
    ap_group = {}
    _interactive_particles: Set[Interactive]
    interact_range: int

    def __init__(self, info: dict[str, Union[str, float, int, Tuple]]) -> None:
        default = {
            'display_priority': ACTIVE_PARTICLE_DISPLAY_PRIORITY,
            'interact_range': INTERACT_RANGE,
        }
        attr = ['interact_range']
        Particle.ID += 1
        for key in default:
            if key not in info:
                info[key] = default[key]
        super().__init__(info)
        for item in attr:
            setattr(self, item, info[item])
        self._interactive_particles = set()
        ActiveParticle.ap_group[self.id] = self

    def action(self) -> None:
        """ AI of this creature, this method should
        be called on every active creature regularly
        """
        raise NotImplementedError

    def update_status(self) -> None:
        # Ignore warning, get_particle_in_radius guarantees to return Particles
        self._interactive_particles = set()
        radius = math.ceil(self.interact_range / TILE_SIZE)
        for particle in get_particles_in_radius(self, radius, Interactive,
                                                False):
            center_x = particle.x + particle.diameter / 2
            center_y = particle.y + particle.diameter / 2
            x_d = pow(center_x - self.x, 2)
            y_d = pow(center_y - self.y, 2)
            if math.sqrt(x_d + y_d) <= pow(self.interact_range, 2) and \
                    particle.can_interact(self):
                self._interactive_particles.add(particle)
        super().update_status()

    def remove(self):
        Particle.remove(self)
        ActiveParticle.ap_group.pop(self.id, None)


class Creature(Living, Particle):
    """
    Description: Particles that are alive

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
            info['display_priority'] = ACTIVE_PARTICLE_DISPLAY_PRIORITY
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
        for item in attr:
            setattr(self, item, info[item])

    def get_texture(self):
        d = math.ceil(self.get_stat("diameter") * public_namespace.scale)
        texture = self.texture
        tup = (texture, (d, d), self.direction, 255, self.color)
        try:
            return Creature.creature_textures[tup].copy()
        except KeyError:
            raw = public_namespace.get_texture_by_info(texture, (d * 2, d * 2),
                                                       self.direction, 255)
            self._draw_color_on_texture(raw)
            Creature.creature_textures[tup] = raw
            return raw.copy()

    def _draw_color_on_texture(self, surface: pygame.Surface) -> None:
        if self.color is not None:
            radius = self.diameter // 2 * public_namespace.scale
            size = surface.get_size()
            cx = int(size[0] / 2)
            cy = int(size[1] / 2)
            pygame.draw.circle(
                surface, self.color, (cx, cy), radius)

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


def colliding_tiles_generator(x: float, y: float,
                              diameter: int, ) -> List[Tuple[int, int]]:
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
    mp = public_namespace.game_map[map_name]
    ps = set()
    for coord in coordinates:
        ps.update(mp[coord[0]][coord[1]].copy())
    return ps


def get_particles_in_radius(particle: Particle, radius=1, tp=None,
                            corner=True) -> List[Particle]:
    """ Return particles in the given radius through Generator """
    x = particle.x + particle.diameter / 2
    y = particle.y + particle.diameter / 2
    row = int(y // TILE_SIZE)
    col = int(x // TILE_SIZE)
    start_row = row - radius
    end_row = row + radius
    start_col = col - radius
    end_col = col + radius

    width = len(public_namespace.game_map[particle.map_name])
    height = len(public_namespace.game_map[particle.map_name][0])
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
                yield Block.block_group[public_namespace.tile_map[particle.map_name][x][
                    y]]
            else:
                ps = public_namespace.game_map[particle.map_name][x][y]
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
