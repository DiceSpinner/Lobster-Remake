from abc import ABC

import pygame
from typing import List, Any, Tuple, Union, Optional
from utilities import Positional, Movable, Collidable, Lightable, Living, \
    Directional, get_direction
from settings import TILE_SIZE, SQUARE, CIRCLE, SHAPES
import os
import math


class Particle(Positional):
    """
    Description: Customized sprites

    === Public Attributes ===
    id: Identifier of the particle.
    pos: A dictionary that stores the position of this particle in the map,
        the key is the name of the map and the values are x-y coordinates.

    display_priority: The display priority of this particle, particles with
        the highest priority will be displayed on top of the screen

    name: Name of this particle (displayed in map txt file)
    """
    ID = 0
    particle_group = {}
    id: int
    display_priority: int
    texture: pygame.Surface
    name: str

    def __init__(self, info: dict[str, Union[str, float, int]]) -> None:
        default = {
            'display_priority': 0,
            'texture': "Lobster-64.png",
            'name': 'particle'
        }
        attr = ['display_priority', 'texture', 'name']
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
        Particle.particle_group[self.id] = self

    def display(self, screen: pygame.Surface,
                location: Tuple[int, int]) -> None:
        screen.blit(self.texture, location)

    def remove(self):
        """ Remove this particle from the game """
        Particle.particle_group.pop(self.id, None)

    def __str__(self):
        return self.name


class Item(Collidable):
    """ Description: An object represents an item in game

    """
    pass


class Creature(Particle, Collidable, Movable, Living, Directional):
    """
    Description: Movable entities

    Additional Attributes:
        speed: Speed of this creature
        active: Whether this creature is active
        color: Displayed color of this creature
    Representation Invariants:

    """
    creature_group = {}
    active: bool
    color: Tuple[int, int, int]

    def __init__(self, info: dict[str, Union[str, float, int, Tuple]]) -> None:
        if "display_priority" not in info:
            info['display_priority'] = 2

        Particle.__init__(self, info)
        Collidable.__init__(self, info)
        Movable.__init__(self, info)
        Directional.__init__(self, info)
        Creature.creature_group[self.id] = self
        self.texture = pygame.transform.scale(self.texture, (self.diameter * 2,
                                                             self.diameter * 2))
        attr = ["active", 'color']
        default = {
            'active': True,
            'color': (255, 255, 255)
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

    def is_dead(self) -> bool:
        return self.death.eval(vars(self))

    def update_status(self) -> None:
        if self.is_dead():
            self.remove()

    def update_position(self, particles: List[Collidable]) -> None:
        x_d = abs(self.vx)
        y_d = abs(self.vy)
        c_x = int(self.x)
        c_y = int(self.y)
        if self.vx == 0 and self.vy == 0:
            return
        if self.vx == 0:
            x_time = 0
            y_time = 1
        elif self.vy == 0:
            x_time = 1
            y_time = 0
        elif abs(self.vx) > abs(self.vy):
            x_time = int(round(abs(self.vx) / abs(self.vy), 0))
            y_time = 1
        elif abs(self.vx) < abs(self.vy):
            x_time = 1
            y_time = int(round(abs(self.vy) / abs(self.vx), 0))
        else:
            x_time, y_time = 1, 1
        while x_d > 0 or y_d > 0:
            if x_d > 0:
                for i in range(x_time):
                    if x_d >= 1:
                        value = self.vx / abs(self.vx)
                        x_d -= 1
                    else:
                        value = self.vx - int(self.vx)
                        x_d = 0
                    self.x += value
                    n_x = int(self.x)
                    if abs(n_x - c_x) >= 1:
                        for particle in particles:
                            if self.detect_collision(particle):
                                self.x -= value
                                x_d = 0
                                break

            if y_d > 0:
                for i in range(y_time):
                    if y_d >= 1:
                        value = self.vy / abs(self.vy)
                        y_d -= 1
                    else:
                        value = self.vy - int(self.vy)
                        y_d = 0
                    self.y += value
                    n_y = int(self.y)
                    if abs(n_y - c_y) >= 1:
                        for particle in particles:
                            if self.detect_collision(particle):
                                self.y -= value
                                y_d = 0
                                break
        self.vx = 0
        self.vy = 0

    def remove(self):
        Particle.remove(self)
        Creature.creature_group.pop(self, None)


class Player(Creature):
    """
    Description: Player class

    Additional Attributes:
        pressed_keys: A list of pressed keys of this player
    Representation Invariants:

    """
    player_group = {}
    pressed_keys: List[int]

    def __init__(self, info: dict[str, Union[str, float, int]]) -> None:
        Creature.__init__(self, info)
        Player.player_group[self.id] = self
        self.pressed_keys = []

    def action(self, player_input: Optional[List[pygame.event.Event]]) -> None:
        for event in player_input:
            if event.type == pygame.KEYDOWN:
                self.pressed_keys.append(event.key)
            elif event.type == pygame.KEYUP:
                self.pressed_keys.remove(event.key)
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

    def remove(self):
        Creature.remove(self)
        Player.player_group.pop(self, None)


class Block(Particle, Collidable, Lightable):
    """

    """

    def __init__(self, info: dict[str, Union[str, float, int]]) -> None:
        Particle.__init__(self, info)
        Collidable.__init__(self, info)
        Lightable.__init__(self, info)
        self.texture = pygame.transform.scale(self.texture, (TILE_SIZE,
                                                             TILE_SIZE))

    def display(self, screen: pygame.Surface,
                location: Tuple[float, float]) -> None:
        screen.blit(self.texture, [location[0], location[1]])

        dark = pygame.Surface((self.diameter,
                               self.diameter))
        dark.fill((0, 0, 0))
        dark.set_alpha(255 - self.brightness)
        # screen.blit(dark, [location[0], location[1]])


class NPC(Creature):
    """ Description: Non-Player Character class

    Additional Attributes:
        reaction_range: The range where this npc will react to other entities
        blocks_in_range: Tiles within the reaction range of this npc
        entities_in_range: Entities within the reaction range of this npc
    Representation Invariants:
    """
    reaction_range: int
    blocks_in_range: List[List[Block]]
    entities_in_range: List[List[List[Union[Creature, Item]]]]
    npc_group = {}

    def __init__(self, info: dict[str, Union[str, float, int]]) -> None:
        Creature.__init__(self, info)
        NPC.npc_group[self.id] = self

    def query_info(self):
        pass

    def action(self, player_input: Optional[List[pygame.event.Event]]) -> None:
        pass
