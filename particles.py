from abc import ABC

import pygame
from typing import List, Any, Tuple, Union
from positional import Positional, Movable
from settings import TILE_SIZE, SQUARE, CIRCLE, SHAPES


class Particle(Positional):
    """
    Description: Customized sprites

    === Public Attributes ===
    id: Identifier of the particle.
    pos: A dictionary that stores the position of this particle in the map,
        the key is the name of the map and the values are x-y coordinates.

    display_priority: The display priority of this particle, particles with
        the highest priority will be displayed on top of the screen

    """
    ID = 0
    particle_group = {}
    id: int
    display_priority: int
    texture: pygame.Surface

    def __init__(self, info: dict[str, Union[str, float, int]]) -> None:
        default = {
            'display_priority': 0,
            'texture': "Lobster.png"
        }
        attr = ['display_priority', 'texture']
        Positional.__init__(self, info)
        self.id = Particle.ID
        Particle.ID += 1
        for key in default:
            if key not in info:
                info[key] = default[key]
        for item in info:
            if item in attr:
                setattr(self, item, info[item])
        self.texture = pygame.image.load(self.texture)
        Particle.particle_group[self.id] = self

    def display(self, screen: pygame.Surface,
                location: Tuple[int, int]) -> None:
        screen.blit(self.texture, location)

    def remove(self):
        """ Remove this particle from the game """
        Particle.particle_group.pop(self.id, None)


class Entity(Particle):
    """
    Description: Particles with collision, lighting and health attributes

    Additional Attributes:
        shape: Shape of this entity
        diameter: Physical diameter of this entity
        light_power: The ability of this entity to produce light
        brightness: brightness of this entity

    Representation Invariants:
        diameter >= 0, the particle is non-collidable when diameter = 0
        shape is one of 'circle', 'rect', 'tri'
        0<= light_power <= 255 and can only be 0 when this entity is
            not a light source
        0<= brightness <= 255
    """
    shape: str
    diameter: int
    light_power: int
    brightness: int
    health: float

    def __init__(self, info: dict[str, Union[str, int, float]]) -> None:
        Particle.__init__(self, info)
        default = {
            'shape': SQUARE,
            'diameter': TILE_SIZE,
            'light_power': 0,
            'brightness': 0,
            'health': 1
        }

        for key in default:
            if key not in info:
                info[key] = default[key]

        attr = ['shape', 'diameter', 'light_power', 'brightness',
                'health']
        for item in info:
            if item in attr:
                setattr(self, item, info[item])

    def display(self, screen: pygame.Surface,
                location: Tuple[int, int]) -> None:
        raise NotImplementedError


class Item(Entity, ABC):
    """ Description: An object represents an item in game

    """
    pass


class Creature(Entity, Movable):
    """
    Description: Movable entities

    Additional Attributes:

    Representation Invariants:

    """
    creature_group = {}

    def __init__(self, info: dict[str, Union[str, float, int]]) -> None:
        Entity.__init__(self, info)
        Creature.creature_group[self.id] = self
        if "display_priority" not in info:
            self.display_priority = 2

    def display(self, screen: pygame.Surface,
                location: Tuple[int, int]) -> None:
        screen.blit(self.texture, [location[0], location[1]])

    def remove(self):
        Particle.remove(self)
        Creature.creature_group.pop(self, None)


class Player(Creature):
    """

    """
    player_group = {}

    def __init__(self, info: dict[str, Union[str, float, int]]) -> None:
        Creature.__init__(self, info)
        Player.player_group[self.id] = self

    def remove(self):
        Creature.remove(self)
        Player.player_group.pop(self, None)


class Block(Entity):
    """

    """

    def display(self, screen: pygame.Surface,
                location: Tuple[float, float]) -> None:
        screen.blit(self.texture, [location[0], location[1]])
        dark = pygame.Surface((self.diameter,
                               self.diameter))
        dark.fill((0, 0, 0))
        dark.set_alpha(255 - self.brightness)
        screen.blit(dark, [location[0], location[1]])

