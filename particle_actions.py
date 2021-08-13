import pygame
import math
from particles import *
from utilities import CombatStats, Living, Manaized, Staminaized, \
    Movable, get_direction, Positional, UpdateReq
from bool_expr import BoolExpr, construct_from_str
from typing import Union, Tuple, List
from error import InvalidConstructionInfo
from settings import *


class Illuminator(ActiveParticle, Lightable):
    """ Active particles that are able to illuminate nearby tiles """

    def __init__(self, info: dict[str, Union[str, float, int]]) -> None:
        super().__init__(info)
        il = {
            'name': 'illuminate',
            'stamina_cost': 0,
            'mana_cost': 0,
            'cooldown': 0,
            'priority': LIGHT_PRIORITY,
            'time': 1,
            'method': self._illuminate
        }
        self.add_movement(il)

    def _illuminate(self):
        tiles = self.get_tiles_in_contact()
        sl = self.get_stat('light_source')
        for tile in tiles:
            ol = tile.get_stat('light_source')
            if ol < sl:
                tile.add_stats({'light_source': sl - ol})


class Puppet(Illuminator, UpdateReq):
    """ A stationary particle used for collision detection/animation

    === Public Attributes ===
    _ self_destroy: Ticks before self-destruction
    - owner: The particle that started this puppet

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
            'self_destroy': int(FPS // 3),
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

    def action(self):
        self.enqueue_movement("illuminate", {})

    def update_status(self) -> None:
        self._self_destroy_counter += 1
        self.sync()
        if self._self_destroy_counter >= self.self_destroy:
            self.remove()

    def sync(self):
        self.map_name = self.owner.map_name
        self.x = self.owner.x - 1 + self.owner.get_stat('diameter') / 2 - \
            self.owner.get_stat('attack_range')
        self.y = self.owner.y - 1 + self.owner.get_stat('diameter') / 2 - \
            self.owner.get_stat('attack_range')


class StandardMoveSet(ActiveParticle, CombatStats, Manaized, Movable,
                      Lightable):
    """ Standard movesets that covers basic moving, offensive and defensive
    movements, must be inherited by other sub-creature classes in order to
    utilize these methods.

    === Public Attributes ===
    - attack_range: The range of basic attacks
    - attack_speed: The number of basic attacks can be performed in a second
    - target: A bool expression that gives info about target
    - attack_texture: The texture of attacks
    - basic_attack_animation: id of the a

    === Private Attributes ===
    - _attack_counter: The counter for basic attack cooldown
    """
    attack_range: int
    attack_speed: float
    attack_texture: dict[str, pygame.Surface]
    target: BoolExpr
    animations: dict[str, Puppet]

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
            'basic_attack_texture': BASIC_ATTACK_TEXTURE,
            'guard_texture': BASIC_ATTACK_TEXTURE
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
            'priority': ATTACK_PRIORITY,
            'texture': info['basic_attack_texture'],
            'time': DEFAULT_ACTION_TIMER,
            'method': self.basic_attack
        }
        mv = {
            'name': 'move',
            'stamina_cost': 0,
            'mana_cost': 0,
            'cooldown': 0,
            'priority': MOVE_PRIORITY,
            'time': DEFAULT_ACTION_TIMER,
            'method': self.move
        }

        moves = [ba, mv]
        for move in moves:
            self.add_movement(move)

    def can_act(self, name: str) -> bool:
        if Manaized.can_act(self, name):
            if name == 'basic_attack':
                return self._attack_counter >= (FPS //
                                                self.get_stat('attack_speed'))
            return True
        return False

    def cooldown_countdown(self) -> None:
        """ Increase the attack counter by 1 per frame """
        Staminaized.cooldown_countdown(self)
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
            'texture': self.actions['basic_attack'].action_texture,
            'owner': self,
            'light_source': self.get_stat('light_source'),
            'x': c2x,
            'y': c2y,
            'solid': False,
            'map_name': self.map_name
        }
        collision_box = Puppet(info)
        living = list(filter(lambda c: isinstance(Particle.particle_group[c],
                                                  Living),
                             get_nearby_particles(collision_box)))
        for entity in living:
            entity = Particle.particle_group[entity]
            if self._is_target(entity) and \
                    collision_box.detect_collision(entity):
                entity.register_damage(self.get_stat('attack_power'))
        self._attack_counter = 0
        return True

    def apply_velocity(self, direction: Union[float, Positional]) -> None:
        """ Move towards the target direction or object """
        if isinstance(direction, Positional):
            direction = get_direction((self.x, self.y), (direction.x,
                                                         direction.y))
        direction = math.radians(direction)
        speed = round(self.get_stat('speed') / FPS, 2)
        self.add_stats(
            {'vx': round(speed * round(math.cos(direction), 2), 2)})
        self.add_stats(
            {'vy': round(- speed * round(math.sin(direction), 2), 2)})

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
                            total = 0
                            break
        return total, current

    def move(self, direction: Union[float, Positional]) -> None:
        self.apply_velocity(direction)
        if self.get_stat("vx") == 0 and self.get_stat("vy") == 0:
            return
        x_d, y_d, c_x, c_y, x_time, y_time = self.calculate_order()
        while x_d > 0 or y_d > 0:
            x_d, c_x = self.direction_increment(x_time, "x",
                                                x_d, c_x)
            y_d, c_y = self.direction_increment(y_time, "y",
                                                y_d, c_y)

    def _is_target(self, particle: Particle) -> bool:
        return self.target.eval(vars(particle))


class Fireball(StandardMoveSet, Illuminator):
    """ A projectile that damages nearby living particles on contact

    === Public Attributes ===
    - self_destruction: Number of seconds before self-destruction
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
        if self._self_destroy_counter >= self.self_destruction * FPS:
            self.destroyed = True

    def update_position(self) -> None:
        x_d, y_d, c_x, c_y, x_time, y_time = self.calculate_order()
        while (x_d > 0 or y_d > 0) and not self.destroyed:
            x_d, c_x = self.direction_increment(x_time, "x",
                                                x_d, c_x)
            y_d, c_y = self.direction_increment(y_time, "y",
                                                y_d, c_y)

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
                self.update_map_position()
                n = int(getattr(self, direction))
                if abs(n - current) >= 1:
                    particles = get_particles_by_tiles(
                        self.map_name,
                        colliding_tiles_generator(self.x, self.y,
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
            self.enqueue_movement("illuminate", {})
        else:
            self.basic_attack(None)
            self.remove()


class ProjectileThrowable(Creature, CombatStats, Manaized):
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
                'texture': info['fireball_texture'],
                'time': DEFAULT_ACTION_TIMER,
                'priority': ATTACK_PRIORITY,
                'method': self.fireball
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
        target_condition = "( obj -> particles.Creature and " + str(
            self.target) + " )"
        info = {
            'diameter': ball_size,
            'shape': self.shape,
            'ignore': construct_from_str(condition),
            'light_source': FIREBALL_BRIGHTNESS,
            'texture': self.actions['fireball'].action_texture,
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
