import pygame

from particles import Creature, Particle, calculate_colliding_tiles, \
    get_nearby_particles, \
    get_particles_by_tiles
from utilities import OffensiveStats, Living, Manaized, Staminaized, Collidable
from bool_expr import BoolExpr, construct_from_str
from typing import Union, Tuple, List
from error import InvalidConstructionInfo
from settings import *


class CollisionBox(Creature):
    """ A stationary particle used to collision detection

    === Public Attributes ===
    _ self_destroy: Ticks before self-destruction
    - owner: The particle that created this collision box

    === Private Attributes ===
    - _self_destroy_counter: self-destruction counter
    """
    target: BoolExpr
    self_destroy: int
    _self_destroy_counter: int
    owner: Particle

    def __init__(self, info: dict[str, Union[str, float, int, Tuple]]) -> None:
        if "display_priority" not in info:
            info['display_priority'] = 1
        super().__init__(info)
        attr = ["self_destroy", "_self_destroy_counter", 'owner']
        default = {
            'self_destroy': int(FPS // 2),
            '_self_destroy_counter': 0,
        }
        for key in default:
            if key not in info:
                info[key] = default[key]
        for item in attr:
            if item in info:
                setattr(self, item, info[item])
            else:
                raise InvalidConstructionInfo

    def action(self, player_input=None) -> None:
        self._self_destroy_counter += 1
        self.sync()
        if self._self_destroy_counter >= self.self_destroy:
            self.health = 0

    def sync(self):
        self.map_name = self.owner.map_name
        if isinstance(self.owner, Collidable):
            self.x = self.owner.x - 1 + self.owner.get_stat('diameter') / 2 - \
                     self.owner.get_stat('attack_range')
            self.y = self.owner.y - 1 + self.owner.get_stat('diameter') / 2 - \
                     self.owner.get_stat('attack_range')
        else:
            self.x = self.owner.x - self.owner.get_stat('attack_range')
            self.y = self.owner.y - self.owner.get_stat('attack_range')

    def remove(self):
        Creature.remove(self)


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

        optional = {
            'basic_attack_texture': BASIC_ATTACK_TEXTURE
        }
        for op in optional:
            if op not in info:
                info[op] = optional[op]
        self._attack_counter = 0
        ba = {
            'name': 'basic_attack',
            'stamina_cost': DEFAULT_ATTACK_STAMINA_COST,
            'mana_cost': DEFAULT_ATTACK_MANA_COST,
            'cooldown': 0,
            'texture': info['basic_attack_texture']
        }
        moves = [ba]
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
            'texture': self.action_textures['basic_attack'],
            'owner': self,
            'light_source': self.get_stat('light_source'),
            'x': c2x,
            'y': c2y,
            'solid': False,
            'map_name': self.map_name
        }
        collision_box = CollisionBox(info)
        living = list(filter(lambda c: isinstance(Particle.particle_group[c],
            Living), get_nearby_particles(collision_box)))
        for entity in living:
            entity = Particle.particle_group[entity]
            if self._is_target(entity) and \
                    collision_box.detect_collision(entity):
                entity.health -= self.get_stat('attack_power')
        self._attack_counter = 0
        return True

    def _is_target(self, particle: Particle) -> bool:
        return self.target.eval(vars(particle))


class Projectile(StandardAttacks):

    def __init__(self, info: dict[str, Union[str, float, int, Tuple, List]]) \
            -> None:
        super().__init__(info)


class Fireball(Projectile):
    """ A projectile that damages nearby living particles on contact

    === Public Attributes ===
    - self_destruction: Number of frames before self-destruction
    - destroyed: Whether this object has been destroyed
    - ignore: A boolexpr that determines which particles to ignore
    === Private Attributes ===
    - _self_destroy_counter: Countdown of self-destruction
    """
    self_destruction: int
    destroyed: bool
    ignore: BoolExpr

    def __init__(self, info: dict[str, Union[str, float, int, Tuple, List]]) \
            -> None:
        super().__init__(info)
        attr = ['self_destruction', 'ignore']
        default = {
            'self_destruction': DEFAULT_PROJECTILE_COUNTDOWN,
            'ignore': construct_from_str(DEFAULT_TARGET)
        }
        for item in default:
            if item not in info:
                info[item] = default[item]
        for a in attr:
            setattr(self, a, info[a])
        self.ignore.substitute(vars(self))
        self.destroyed = False
        self._self_destroy_counter = 0

    def count_down(self):
        self._self_destroy_counter += 1
        if self._self_destroy_counter >= self.self_destruction:
            self.destroyed = True

    def update_position(self) -> None:
        x_d, y_d, c_x, c_y, x_time, y_time = self.calculate_order()
        while (x_d > 0 or y_d > 0) and not self.destroyed:
            x_d, c_x = self.direction_increment(x_time, "x",
                                                x_d, c_x)
            y_d, c_y = self.direction_increment(y_time, "y",
                                                y_d, c_y)
        self.update_map_position()

    def direction_increment(self, time: int, direction: str, total: float,
                            current: int) -> Tuple[float, float]:
        """ Increment the position of the particle in given direction """
        vel = 'v' + direction
        for i in range(time):
            if total > 0:
                if total >= 1:
                    value = self.get_stat(vel) / abs(self.get_stat(vel))
                    total -= 1
                else:
                    value = self.get_stat(vel) - int(self.get_stat(vel))
                    total = 0
                setattr(self, direction, getattr(self, direction) + value)
                n = int(getattr(self, direction))
                if abs(n - current) >= 1:
                    particles = get_particles_by_tiles(
                        self.map_name,
                        calculate_colliding_tiles(self.x, self.y,
                                                  self.diameter))
                    for particle in particles:
                        particle = Particle.particle_group[particle]
                        attr = vars(particle)
                        attr['obj'] = particle
                        if not self.ignore.eval(attr) and \
                                (self._is_target(particle) or particle.solid) \
                                and self.detect_collision(particle):
                            self.destroyed = True
                            break
        return total, current

    def action(self, optional=None):
        if not self.destroyed:
            self.count_down()
            self.move(self.direction)
            self.update_position()
        else:
            self.basic_attack(None)
            self.health = 0


class ProjectileThrowable(Creature, OffensiveStats, Manaized):
    """
    """
    target: BoolExpr
    fireball_explosion_range: int

    def __init__(self, info: dict[str, Union[str, float, int, BoolExpr]]) -> \
            None:
        attr = ['target', 'fireball_explosion_range']
        default = {
            'target': construct_from_str(DEFAULT_TARGET),
            "fireball_explosion_range": FIREBALL_EXPLOSION_RANGE
        }
        for key in default:
            if key not in info:
                info[key] = default[key]
        for a in attr:
            setattr(self, a, info[a])
        super().__init__(info)
        self.target.substitute(vars(self))
        optional = {
            'fireball_texture': FIREBALL_TEXTURE
        }
        for op in optional:
            if op not in info:
                info[op] = optional[op]
        moves = [
            {
                'name': 'fireball',
                'stamina_cost': DEFAULT_ABILITY_STAMINA_COST,
                'mana_cost': DEFAULT_ABILITY_MANA_COST,
                'cooldown': DEFAULT_ABILITY_COOLDOWN,
                'texture': info['fireball_texture']
            }
        ]
        for move in moves:
            self.add_movement(move)

    def fireball(self) -> None:
        """ Damage every nearby creatures inside the explosion range of
        the fireball
        """
        c1x = self.x - 1 + self.get_stat('diameter') / 2
        c1y = self.y - 1 + self.get_stat('diameter') / 2
        ball_size = int(self.get_stat('fireball_explosion_range'))
        c2x = c1x - ball_size // 2
        c2y = c1y - ball_size // 2
        condition = "( id = self.id or id = " + str(self.id) + " )"
        target_condition = "( obj -> particles.Creature and " + str(self.target) + " )"
        info = {
            'diameter': ball_size,
            'shape': self.shape,
            'ignore': construct_from_str(condition),
            'light_source': FIREBALL_BRIGHTNESS,
            'texture': self.action_textures['fireball'],
            'target': construct_from_str(target_condition),
            'attack_damage': self.get_stat('ability_power'),
            'attack_range': self.get_stat('fireball_explosion_range'),
            'speed': DEFAULT_PROJECTILE_SPEED,
            'direction': self.direction,
            'x': c2x,
            'y': c2y,
            'map_name': self.map_name,
            'basic_attack_texture': 'fireball_explosion.png'
        }
        Fireball(info)
