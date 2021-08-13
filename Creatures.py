from particle_actions import StandardMoveSet, ProjectileThrowable, Illuminator
from particles import Creature
from typing import List, Tuple, Union, Optional
import pygame


class Player(StandardMoveSet, ProjectileThrowable, Illuminator):
    """
    Description: Player class

    === Public Attribute ===
    - light_on: Whether the player is illuminating its surroundings


    Representation Invariants:

    """
    player_group = {}
    mouse_buttons: Tuple[int, int, int]
    light_on: bool

    def __init__(self, info: dict[str, Union[str, float, int]]) -> None:
        super().__init__(info)
        Player.player_group[self.id] = self
        self.mouse_buttons = (0, 0, 0)
        self.light_on = True

    def action(self) -> None:
        self.mouse_buttons = pygame.mouse.get_pressed(3)
        pressed_keys = pygame.key.get_pressed()
        effective_directions = []
        if pressed_keys[pygame.K_w] and not pressed_keys[pygame.K_s]:
            effective_directions.append(pygame.K_w)
        elif not pressed_keys[pygame.K_w] and pressed_keys[pygame.K_s]:
            effective_directions.append(pygame.K_s)

        if pressed_keys[pygame.K_d] and not pressed_keys[pygame.K_a]:
            effective_directions.append(pygame.K_d)
        elif not pressed_keys[pygame.K_d] and pressed_keys[pygame.K_a]:
            effective_directions.append(pygame.K_a)
        if len(effective_directions) > 0:
            if pygame.K_w in effective_directions:
                if pygame.K_a in effective_directions:
                    direction = 135
                elif pygame.K_d in effective_directions:
                    direction = 45
                else:
                    direction = 90
            elif pygame.K_s in effective_directions:
                if pygame.K_a in effective_directions:
                    direction = 225
                elif pygame.K_d in effective_directions:
                    direction = 315
                else:
                    direction = 270
            elif pygame.K_a in effective_directions:
                direction = 180
            else:
                direction = 0
            self.enqueue_movement('move', {"direction": direction})
        # light
        if self.light_on:
            self.enqueue_movement('illuminate', {})
        # attack
        if self.mouse_buttons[0] == 1:
            self.enqueue_movement('basic_attack', {})
        if pressed_keys[pygame.K_q]:
            self.enqueue_movement('fireball', {})

    def remove(self):
        Creature.remove(self)
        Player.player_group.pop(self.id, None)


class NPC(StandardMoveSet, ProjectileThrowable):
    """ Description: Non-Player Character class

    Additional Attributes:

    Representation Invariants:
    """
    npc_group = {}

    def __init__(self, info: dict[str, Union[str, float, int]]) -> None:
        super().__init__(info)
        NPC.npc_group[self.id] = self

    def action(self) -> None:
        self.enqueue_movement('basic_attack', {})
        # self.enqueue_movement("move", {'direction': self.direction})
        # self.enqueue_movement('fireball', {})

    def remove(self):
        Creature.remove(self)
        NPC.npc_group.pop(self.id, None)
