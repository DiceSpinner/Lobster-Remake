from particle_actions import StandardMoveSet, ProjectileThrowable, Illuminator
from particles import Creature, AnimatedParticle
from typing import List, Tuple, Union, Optional
import public_namespace
import pygame


class Player(StandardMoveSet, ProjectileThrowable, Illuminator,
             AnimatedParticle, Creature):
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
        pressed_keys = public_namespace.input_handler.get_key_pressed()
        key_up = public_namespace.input_handler.get_key_up()

        effective_directions = []
        if pygame.K_w in pressed_keys and pygame.K_s not in pressed_keys:
            effective_directions.append(pygame.K_w)
        elif pygame.K_w not in pressed_keys and pygame.K_s in pressed_keys:
            effective_directions.append(pygame.K_s)

        if pygame.K_d in pressed_keys and pygame.K_a not in pressed_keys:
            effective_directions.append(pygame.K_d)
        elif pygame.K_d not in pressed_keys and pygame.K_a in pressed_keys:
            effective_directions.append(pygame.K_a)
        if pygame.K_LSHIFT in pressed_keys:
            self.enqueue_action("speed_up", {})
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
            self.enqueue_action('move', {"direction": direction})
        # light
        if self.light_on:
            self.enqueue_action('illuminate', {})
        # attack
        if self.mouse_buttons[0] == 1:
            self.enqueue_action('basic_attack', {})
        elif self.mouse_buttons[2] == 1:
            self.enqueue_action('guard', {})
        if pygame.K_SPACE in pressed_keys:
            self.enqueue_action('fireball', {})
        # interact
        for particle in self._interactive_particles:
            if pygame.K_f in key_up:
                particle.upon_interact(self)
            break

    def remove(self):
        Creature.remove(self)
        Player.player_group.pop(self.id, None)


class NPC(StandardMoveSet, ProjectileThrowable, Creature):
    """ Description: Non-Player Character class

    Additional Attributes:

    Representation Invariants:
    """
    npc_group = {}

    def __init__(self, info: dict[str, Union[str, float, int]]) -> None:
        super().__init__(info)
        NPC.npc_group[self.id] = self

    def action(self) -> None:
        # self.enqueue_action('basic_attack', {})
        self.direction += 1
        if self.direction == 360:
            self.direction = 0
        # self.enqueue_action("move", {'direction': self.direction})
        self.enqueue_action('fireball', {})
        pass

    def remove(self):
        Creature.remove(self)
        NPC.npc_group.pop(self.id, None)
