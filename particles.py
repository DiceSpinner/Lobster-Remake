from abc import ABC

import pygame
from typing import List, Any, Tuple, Union, Optional
from utilities import Positional, Movable, Collidable, Lightable, Living
from settings import TILE_SIZE, SQUARE, CIRCLE, SHAPES
import os


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


class Creature(Particle, Collidable, Movable, Living):
    """
    Description: Movable entities

    Additional Attributes:

    Representation Invariants:

    """
    creature_group = {}

    def __init__(self, info: dict[str, Union[str, float, int]]) -> None:
        if "display_priority" not in info:
            info['display_priority'] = 2
        Particle.__init__(self, info)
        Collidable.__init__(self, info)
        Movable.__init__(self, info)
        Creature.creature_group[self.id] = self

    def display(self, screen: pygame.Surface,
                location: Tuple[int, int]) -> None:
        screen.blit(self.texture, [location[0], location[1]])
        dark = pygame.Surface((self.diameter,
                               self.diameter))
        dark.fill((0, 0, 0))
        dark.set_alpha(100)
        screen.blit(dark, [location[0], location[1]])
        pygame.draw.circle(screen, (0, 255, 255), (location[0] + self.diameter // 2, location[1] + self.diameter // 2), self.diameter // 2)

    def action(self, player_input: Optional[List[pygame.event.Event]]) -> None:
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
                    if x_d > 1:
                        value = self.vx / abs(self.vx)
                        x_d -= 1
                    else:
                        value = self.vx % int(self.vx)
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
                    if y_d > 1:
                        value = self.vy / abs(self.vy)
                        y_d -= 1
                    else:
                        value = self.vy % int(self.vy)
                        y_d = 0
                    self.y += value
                    n_y = int(self.y)
                    if abs(n_y - c_y) >= 1:
                        for particle in particles:
                            if self.detect_collision(particle):
                                self.y -= value
                                y_d = 0
                                break





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
        self.texture = pygame.transform.scale(self.texture, (self.diameter,
                                                             self.diameter))

    def action(self, player_input: Optional[List[pygame.event.Event]]) -> None:
        for event in player_input:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w:
                    self.vy = -2.1
                elif event.key == pygame.K_a:
                    self.vx = -2.1
                elif event.key == pygame.K_s:
                    self.vy = 2.1
                elif event.key == pygame.K_d:
                    self.vx = 2.1
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_w:
                    self.vy = 0
                elif event.key == pygame.K_a:
                    self.vx = 0
                elif event.key == pygame.K_s:
                    self.vy = 0
                elif event.key == pygame.K_d:
                    self.vx = 0

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

