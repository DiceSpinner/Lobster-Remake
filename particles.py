from __future__ import annotations
import pygame
from typing import List, Any, Tuple, Union, Optional, Generic, TypeVar
from utilities import Positional, Movable, Collidable, Lightable, Living, \
    Directional, Attackable, get_direction
from settings import TILE_SIZE, SQUARE, CIRCLE, SHAPES
from bool_expr import BoolExpr, construct_from_str
import os
from settings import *
from error import AttackOnCoolDownError, InvalidConstructionInfo
import math


class Particle(Positional):
    """
    Description: Customized sprites

    === Public Attributes ===
    - id: Identifier of the particle.
    - pos: A dictionary that stores the position of this particle in the map,
        the key is the name of the map and the values are x-y coordinates.

    - display_priority: The display priority of this particle, particles with
        the highest priority will be displayed on top of the screen

    - name: Name of this particle (displayed in map txt file)

    === Private Attributes ===
    -
    """
    ID = 0
    particle_group = {}
    light_particles = {}
    id: int
    display_priority: int
    texture: pygame.Surface
    name: str
    detection_radius: int
    _surrounding_tiles: dict[int, dict[int, Particle]]
    _surrounding_entities: dict[int, dict[int, List[Particle]]]

    def __init__(self, info: dict[str, Union[str, float, int]]) -> None:
        default = {
            'display_priority': DEFAULT_DISPLAY_PRIORITY,
            'texture': DEFAULT_PARTICLE_TEXTURE,
            'name': DEFAULT_PARTICLE_NAME,
            'detection_radius': DEFAULT_DETECTION_RADIUS
        }
        attr = ['display_priority', 'texture', 'name', 'detection_radius']
        Positional.__init__(self, info)
        self.id = Particle.ID
        Particle.ID += 1
        for key in default:
            if key not in info:
                info[key] = default[key]
        for item in info:
            if item in attr:
                setattr(self, item, info[item])
        self.texture = pygame.image.load(
            os.path.join("assets/images", self.texture))
        self._surrounding_tiles = []
        self._surrounding_entities = []
        Particle.particle_group[self.id] = self

    def display(self, screen: pygame.Surface,
                location: Tuple[int, int]) -> None:
        screen.blit(self.texture, location)

    def remove(self):
        """ Remove this particle from the game """
        Particle.particle_group.pop(self.id, None)

    def update_surroundings(self, tiles: dict[int, dict[int, Particle]],
                            entities: dict[int, dict[int, List[Particle]]]):
        self._surrounding_tiles = tiles
        self._surrounding_entities = entities

    def get_adjacent_tiles(self, diagonal=False) -> List[Particle]:
        if isinstance(self, Collidable):
            center_x = int((self.x - 1 + self.diameter / 2) // TILE_SIZE)
            center_y = int((self.y - 1 + self.diameter / 2) // TILE_SIZE)
        else:
            center_x = int((self.x // TILE_SIZE))
            center_y = int((self.y // TILE_SIZE))

        left = (center_x - 1, center_y)
        top = (center_x, center_y - 1)
        right = (center_x + 1, center_y)
        down = (center_x, center_y + 1)
        returning = [left, top, right, down]
        if diagonal:
            top_left = (center_x - 1, center_y - 1)
            top_right = (center_x + 1, center_y - 1)
            bottom_right = (center_x + 1, center_y + 1)
            bottom_left = (center_x - 1, center_y + 1)
            returning += [top_right, top_left, bottom_right, bottom_left]
        lst = []
        for item in returning:
            if item[1] in self._surrounding_tiles:
                if item[0] in self._surrounding_tiles[item[1]]:
                    lst.append(self._surrounding_tiles[item[1]][item[0]])
        return lst

    def __str__(self):
        return self.name


class Item(Collidable, Particle):
    """ Description: An object represents an item in game

    """
    pass


class Attack(Particle, Collidable, Attackable):
    """ A stationary area that deals damage to living objects colliding with it

    === Public Attributes ===
    _ self_destroy: Ticks before self-destruction
    - target: A bool expression that evaluates based on passed in particle info
        to determine whether it should be the target of the orb.
    - owner: The particle that launched this attack

    === Private Attributes ===
    - _self_destroy_counter: self-destruction counter
    """
    target: BoolExpr
    self_destroy: int
    _self_destroy_counter: int
    owner: Particle
    attacks = {}

    def __init__(self, info: dict[str, Union[str, float, int, Tuple]]) -> None:
        if "display_priority" not in info:
            info['display_priority'] = 1

        Particle.__init__(self, info)
        Collidable.__init__(self, info)
        Attackable.__init__(self, info)
        Attack.attacks[self.id] = self
        attr = ["self_destroy", "_self_destroy_counter", 'target', 'owner']
        default = {
            'self_destroy': int(FPS // 2),
            '_self_destroy_counter': 0,
            'target': []
        }
        for key in default:
            if key not in info:
                info[key] = default[key]
        for item in attr:
            if item in info:
                setattr(self, item, info[item])
            else:
                raise InvalidConstructionInfo
        self._attack_counter = self.attack_speed

    def attack(self, targets: Optional[List[Living]]) -> None:
        """ Perform an attack and reset the attack counter
        """
        if not self.can_attack():
            raise AttackOnCoolDownError
        for target in targets:
            assert isinstance(target, Collidable)
            if self.is_target(target) and self.detect_collision(target):
                target.health -= self.attack_power
        self._attack_counter += 1

    def can_attack(self) -> bool:
        return self._attack_counter == self.attack_speed

    def count(self) -> None:
        # override
        if self._attack_counter < self.attack_speed:
            self._attack_counter += 1
        self._self_destroy_counter += 1
        if self._self_destroy_counter >= self.self_destroy:
            self.remove()

    def sync(self):
        self.map_name = self.owner.map_name
        self.x = self.owner.x
        self.y = self.owner.y

    def is_target(self, target: Any):
        return self.target.eval(vars(target))

    def display(self, screen: pygame.Surface,
                location: Tuple[int, int]) -> None:
        screen.blit(self.texture, location)

    def remove(self):
        Particle.remove(self)
        Attack.attacks.pop(self.id, None)


class Creature(Particle, Collidable, Movable, Living, Directional, Lightable):
    """
    Description: Movable entities

    Additional Attributes:
        light_on: Whether this creature is illuminating its surroundings
        active: Whether this creature is active
        color: Displayed color of this creature
    Representation Invariants:

    """
    creature_group = {}
    active: bool
    color: Tuple[int, int, int]
    light_on: bool

    def __init__(self, info: dict[str, Union[str, float, int, Tuple]]) -> None:
        if "display_priority" not in info:
            info['display_priority'] = 2

        Particle.__init__(self, info)
        Collidable.__init__(self, info)
        Movable.__init__(self, info)
        Lightable.__init__(self, info)
        Directional.__init__(self, info)
        Living.__init__(self, info)
        Creature.creature_group[self.id] = self
        self.texture = pygame.transform.scale(self.texture, (self.diameter * 2,
                                                             self.diameter * 2))
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

    def display(self, screen: pygame.Surface,
                location: Tuple[int, int]) -> None:
        radius = self.diameter / 2
        texture = pygame.transform.rotate(self.texture, self.direction)
        centre_x = location[0] + radius - 1
        centre_y = location[1] + radius - 1
        size = texture.get_size()
        cx = centre_x - size[0] / 2 + radius
        cy = centre_y - size[1] / 2
        # texture = self.texture
        screen.blit(texture, [cx - radius, cy])
        # dark = pygame.Surface((self.diameter,
        #                       self.diameter))
        # dark.fill((0, 0, 0))
        # dark.set_alpha(100)
        # screen.blit(dark, [location[0], location[1]])

        if self.shape == CIRCLE:
            pygame.draw.circle(
                screen, self.color, (location[0] + self.diameter // 2, location[
                    1] + radius), radius)
        elif self.shape == SQUARE:
            pygame.draw.rect(
                screen, self.color, pygame.Rect(location[0] + radius, location[
                    1] + radius, radius, radius))

    def aim(self, obj: Positional) -> None:
        cx = self.x + self.diameter / 2 - 1
        cy = self.y + self.diameter / 2 - 1
        obj = (obj.x, obj.y)
        if isinstance(obj, Collidable):
            obj = (obj.x + obj.diameter / 2 - 1, obj.y + obj.diameter / 2 - 1)
        self.direction = get_direction((cx, cy), obj)

    def action(self, player_input: Optional[List[pygame.event.Event]]) -> None:
        """ AI of this creature, this method should
        be called on every active creature regularly
        """
        raise NotImplementedError

    def update_position(self) -> None:
        x_d = abs(self.get_stat('vx'))
        y_d = abs(self.get_stat('vy'))
        c_x = int(self.x)
        c_y = int(self.y)
        particles = []
        for row in self._surrounding_tiles:
            row = self._surrounding_tiles[row]
            for p in row:
                particles.append(row[p])
        for row in self._surrounding_entities:
            row = self._surrounding_entities[row]
            for col in row:
                col = row[col]
                for item in col:
                    if isinstance(item, Collidable) and item.solid:
                        particles.append(item)

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
        while x_d > 0 or y_d > 0:
            if x_d > 0:
                for i in range(x_time):
                    if x_d >= 1:
                        value = self.get_stat('vx') / abs(self.get_stat('vx'))
                        x_d -= 1
                    else:
                        value = self.get_stat('vx') - int(self.get_stat('vx'))
                        x_d = 0
                    self.x += value
                    n_x = int(self.x)
                    if abs(n_x - c_x) >= 1:
                        for particle in particles:
                            if particle.solid and self.detect_collision(
                                    particle):
                                self.x -= value
                                x_d = 0
                                break

            if y_d > 0:
                for i in range(y_time):
                    if y_d >= 1:
                        value = self.get_stat('vy') / abs(self.get_stat('vy'))
                        y_d -= 1
                    else:
                        value = self.get_stat('vy') - int(self.get_stat('vy'))
                        y_d = 0
                    self.y += value
                    n_y = int(self.y)
                    if abs(n_y - c_y) >= 1:
                        for particle in particles:
                            if particle.solid and self.detect_collision(
                                    particle):
                                self.y -= value
                                y_d = 0
                                break

    def light(self):
        tile = self.get_tile_in_contact()
        assert isinstance(tile, Lightable)
        sl = self.get_stat('light_source')
        ol = tile.get_stat('light_source')
        if ol < sl:
            tile.add_stats({'light_source': sl - ol})

    def die(self):
        self.remove()

    def remove(self):
        Particle.remove(self)
        Creature.creature_group.pop(self, None)

    def get_tile_in_contact(self) -> Particle:
        col = int((self.x - 1 + self.diameter / 2) // TILE_SIZE)
        row = int((self.y - 1 + self.diameter / 2) // TILE_SIZE)
        return self._surrounding_tiles[row][col]


class Player(Creature, Attackable):
    """
    Description: Player class

    Additional Attributes:
        pressed_keys: A list of pressed keys of this player

    Representation Invariants:

    """
    player_group = {}
    pressed_keys: List[int]
    mouse_buttons: Tuple[int, int, int]

    def __init__(self, info: dict[str, Union[str, float, int]]) -> None:
        Creature.__init__(self, info)
        Attackable.__init__(self, info)
        Player.player_group[self.id] = self
        self.pressed_keys = []
        self.mouse_buttons = (0, 0, 0)

    def action(self, player_input: Optional[List[pygame.event.Event]]) -> None:
        for event in player_input:
            if event.type == pygame.KEYDOWN:
                if event.key not in self.pressed_keys:
                    self.pressed_keys.append(event.key)
            elif event.type == pygame.KEYUP:
                self.pressed_keys.remove(event.key)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.mouse_buttons = pygame.mouse.get_pressed(3)
        effective_directions = []
        for key in self.pressed_keys:
            if key == pygame.K_w or key == pygame.K_a:
                effective_directions.append(key)
            elif key == pygame.K_s:
                if pygame.K_w not in effective_directions:
                    effective_directions.append(key)
                else:
                    effective_directions.remove(pygame.K_w)
            elif key == pygame.K_d:
                if pygame.K_a not in effective_directions:
                    effective_directions.append(key)
                else:
                    effective_directions.remove(pygame.K_a)
        if pygame.K_w in effective_directions:
            if pygame.K_a in effective_directions:
                self.move(135)
            elif pygame.K_d in effective_directions:
                self.move(45)
            else:
                self.move(90)
        elif pygame.K_s in effective_directions:
            if pygame.K_a in effective_directions:
                self.move(225)
            elif pygame.K_d in effective_directions:
                self.move(315)
            else:
                self.move(270)
        elif pygame.K_a in effective_directions:
            self.move(180)
        elif pygame.K_d in effective_directions:
            self.move(0)

        # light

        # attack
        if self.can_attack():
            if self.mouse_buttons[0] == 1:
                self.attack(None)
        self.update_position()

    def attack(self, targets: Optional[List[Living]]) -> None:
        """ Perform an attack and reset the attack counter """
        c1x = self.x - 1 + self.diameter / 2
        c1y = self.y - 1 + self.diameter / 2
        c2x = c1x - self.get_stat('attack_range')
        c2y = c1y - self.get_stat('attack_range')
        target = construct_from_str("( not id = " + str(self.id) + " )")
        info = {
            'diameter': self.get_stat('attack_range') * 2,
            'shape': self.shape,
            'attack_power': self.get_stat('attack_power'),
            'texture': 'attack_circle.png',
            'x': c2x,
            'y': c2y,
            'map_name': self.map_name,
            'owner': self,
            'target': target,
            'solid': False
        }
        Attack(info)
        self._attack_counter = 0

    def remove(self):
        Creature.remove(self)
        Player.player_group.pop(self, None)


class Block(Particle, Collidable, Lightable):
    """

    """
    block_group = {}

    def __init__(self, info: dict[str, Union[str, float, int]]) -> None:
        Particle.__init__(self, info)
        Collidable.__init__(self, info)
        Lightable.__init__(self, info)
        self.texture = pygame.transform.scale(self.texture, (TILE_SIZE,
                                                             TILE_SIZE))
        Block.block_group[self.id] = self

    def remove(self):
        Particle.remove(self)
        Block.block_group.pop(self.id, None)

    def light(self):
        self.enlighten(self)
        if self.get_stat('brightness') > 0:
            blocks = self.get_adjacent_tiles()
            # print(len(blocks))
            for block in blocks:
                assert isinstance(block, Block)
                if block.get_stat('brightness') < self.get_stat('brightness'):
                    self.enlighten(block)
                    block.light()


class NPC(Creature):
    """ Description: Non-Player Character class

    Additional Attributes:

    Representation Invariants:
    """
    npc_group = {}

    def __init__(self, info: dict[str, Union[str, float, int]]) -> None:
        Creature.__init__(self, info)
        NPC.npc_group[self.id] = self

    def query_info(self):
        pass

    def action(self, player_input: Optional[List[pygame.event.Event]]) -> None:
        pass
