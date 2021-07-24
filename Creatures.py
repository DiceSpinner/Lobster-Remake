from particle_actions import StandardAttacks, ProjectileThrowable
from particles import Creature
from typing import List, Tuple, Union, Optional
import pygame


class Player(StandardAttacks, ProjectileThrowable):
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
        super().__init__(info)
        Player.player_group[self.id] = self
        self.pressed_keys = []
        self.mouse_buttons = (0, 0, 0)

    def action(self, player_input: Optional[List[pygame.event.Event]]) -> None:
        self.mouse_buttons = pygame.mouse.get_pressed(3)
        for event in player_input:
            if event.type == pygame.KEYDOWN:
                if event.key not in self.pressed_keys:
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

        # light

        # attack
        if self.mouse_buttons[0] == 1:
            self.perform_act('basic_attack')
        if pygame.K_q in self.pressed_keys:
            self.perform_act('fireball')
        self.update_position()

    def remove(self):
        Creature.remove(self)
        Player.player_group.pop(self.id, None)


class NPC(StandardAttacks):
    """ Description: Non-Player Character class

    Additional Attributes:

    Representation Invariants:
    """
    npc_group = {}

    def __init__(self, info: dict[str, Union[str, float, int]]) -> None:
        super().__init__(info)
        NPC.npc_group[self.id] = self

    def action(self, player_input: Optional[List[pygame.event.Event]]) -> None:
        self.perform_act('basic_attack')
        self.update_position()

    def remove(self):
        Creature.remove(self)
        NPC.npc_group.pop(self.id, None)
