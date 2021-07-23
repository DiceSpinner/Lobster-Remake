import pygame

from particles import Creature, CollisionBox
from utilities import OffensiveStats, Living, Manaized, Staminaized
from bool_expr import BoolExpr, construct_from_str
from typing import Union, Tuple, List
from settings import *


class StandardAttacks(Creature, OffensiveStats, Manaized):
    """ Creatures with a melee AOE sweep attack implementation of the attackable
    method, must be inherited by other sub-creature classes in order to utilize
    the methods.

    === Public Attributes ===
    - attack_range: The range of basic attacks
    - attack_speed: The number of basic attacks can be performed in a second
    - target: A bool expression that gives info about target
    - attack_texture: The texture of attacks

    === Private Attributes ===
    - _attack_counter: The counter for basic attack cooldown
    """
    attack_range: int
    attack_speed: float
    attack_texture: dict[str, pygame.Surface]
    target: BoolExpr

    def __init__(self, info: dict[str, Union[str, float, int]]) -> None:
        attr = ['attack_speed', 'attack_range', 'target']
        default = {
            'attack_speed': DEFAULT_ATTACK_SPEED,
            'attack_range': DEFAULT_ATTACK_RANGE,
            'target': construct_from_str(DEFAULT_TARGET)
        }
        for key in default:
            if key not in info:
                info[key] = default[key]
        for a in attr:
            setattr(self, a, info[a])
        super().__init__(info)
        self.target.substitute(vars(self))

        self._attack_counter = 0
        moves = [
            {
                'name': 'basic_attack',
                'stamina_cost': DEFAULT_ATTACK_STAMINA_COST,
                'mana_cost': DEFAULT_ATTACK_MANA_COST,
                'cooldown': 0
            }
        ]
        for move in moves:
            self.add_movement(move)

    def can_act(self, name: str) -> bool:
        if Manaized.can_act(self, name):
            if name == 'basic_attack':
                return self._attack_counter >= (FPS //
                                                self.get_stat('attack_speed'))
            return True
        return False

    def count(self) -> None:
        """ Increase the attack counter by 1 per frame """
        Staminaized.count(self)
        self._attack_counter += 1

    def basic_attack(self, target=None) -> bool:
        """ Damage every nearby creatures within the attack range """
        c1x = self.x - 1 + self.get_stat('diameter') / 2
        c1y = self.y - 1 + self.get_stat('diameter') / 2
        c2x = c1x - self.get_stat('attack_range')
        c2y = c1y - self.get_stat('attack_range')
        info = {
            'diameter': self.get_stat('attack_range') * 2 + 1,
            'shape': self.shape,
            'texture': 'attack_circle.png',
            'owner': self,
            'x': c2x,
            'y': c2y,
            'map_name': self.map_name
        }
        collision_box = CollisionBox(info)
        for entity in self.get_adjacent_entities(True):
            if isinstance(entity, Creature) and self._is_target(entity):
                if collision_box.detect_collision(entity):
                    entity.health -= self.get_stat('attack_power')
        self._attack_counter = 0
        return True

    def _is_target(self, particle: Creature) -> bool:
        return self.target.eval(vars(particle))


class Projectile(StandardAttacks):
    """ A projectile that damages nearby living particles on contact

    === Public Attributes ===
    - avoid
    - dead
    """
    avoid: List[int]
    dead: bool

    def __init__(self, info: dict[str, Union[str, float, int, Tuple, List]]) \
            -> None:
        super().__init__(info)
        self.avoid = info['avoid']
        self.dead = False

    def is_dead(self) -> bool:
        return self.dead

    def action(self, optional=None):
        self.move(self.direction)
        self.update_position()


class ProjectileThrowable(Creature, OffensiveStats, Manaized):
    """
    """
    target: BoolExpr
    explosion_diameter: int

    def __init__(self, info: dict[str, Union[str, float, int, BoolExpr]]) -> \
            None:
        attr = ['target']
        default = {
            'target': construct_from_str(DEFAULT_TARGET)
        }
        for key in default:
            if key not in info:
                info[key] = default[key]
        for a in attr:
            setattr(self, a, info[a])
        super().__init__(info)
        self.target.substitute(vars(self))

        moves = [
            {
                'name': 'fireball',
                'stamina_cost': DEFAULT_ABILITY_STAMINA_COST,
                'mana_cost': DEFAULT_ABILITY_MANA_COST,
                'cooldown': DEFAULT_ABILITY_COOLDOWN
            }
        ]
        for move in moves:
            self.add_movement(move)

    def fireball(self):
        """ Damage every nearby creatures inside the explosion range of
        the fireball
        """
        c1x = self.x - 1 + self.get_stat('diameter') / 2
        c1y = self.y - 1 + self.get_stat('diameter') / 2
        exd = self.get_stat('explosion_diameter')
        c2x = c1x - exd
        c2y = c1y - exd
        info = {
            'diameter': exd,
            'shape': self.shape,
            'texture': 'fireball.png',
            'target': self.target,
            'attack_damage': self.ability_power,
            'speed': DEFAULT_PROJECTILE_SPEED,
            'direction': self.direction,
            'x': c2x,
            'y': c2y,
            'map_name': self.map_name
        }
        Projectile(info)
