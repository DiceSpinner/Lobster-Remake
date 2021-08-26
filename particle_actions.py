import pygame
import math
import particles
from particles import *
from utilities import CombatStats, Living, Manaized, Staminaized, get_direction\
    , Positional
from expression_trees import BoolExpr, MultiObjectsEvaluator, \
    ObjectAttributeEvaluator
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
        self.add_action(il)

    def _illuminate(self):
        tiles = self.get_tiles_in_contact()
        sl = self.get_stat('light_source')
        for tile in tiles:
            ol = tile.get_stat('light_source')
            if ol < sl:
                tile.add_stats({'light_source': sl - ol})


class Puppet(Illuminator):
    """ A stationary particle used for collision detection/animation

    === Public Attributes ===
    _ self_destroy: Ticks before self-destruction
    - owner: The particle that created this puppet
    - sync_offset: The position difference between self and the owner particle

    === Private Attributes ===
    - _self_destroy_counter: self-destruction counter
    """
    target: BoolExpr
    self_destroy: int
    _self_destroy_counter: int
    sync_offset: Tuple[int, int]
    owner: Particle

    def __init__(self, info: dict[str, Union[str, float, int, Tuple]]) -> None:
        if "display_priority" not in info:
            info['display_priority'] = 1
        super().__init__(info)
        attr = ["self_destroy", "_self_destroy_counter", 'owner', 'sync_offset']
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
        self.enqueue_action("illuminate", {})

    def delay_destruction(self, frames: int) -> None:
        """ Delay self-destruction for a certain amount of frames """
        self._self_destroy_counter -= frames

    def update_status(self) -> None:
        self._self_destroy_counter += 1
        self.sync()
        if self._self_destroy_counter >= self.self_destroy:
            self.remove()

    def sync(self):
        self.map_name = self.owner.map_name
        self.x = self.owner.x + self.sync_offset[0]
        self.y = self.owner.y + self.sync_offset[1]
        self.update_map_position()


class StandardMoveSet(DisplacableParticle, ActiveParticle, CombatStats, Manaized):
    """ Standard movesets that covers basic moving, offensive and defensive
    movements, must be inherited by other sub-creature classes in order to
    utilize these methods.

    === Public Attributes ===
    - attack_range: The range of basic attacks
    - attack_speed: The number of basic attacks can be performed in a second
    - target: Description of the target of the attacks
    - attack_texture: The texture of attacks
    - animations: Animations for actions
    - speed: Speed of the particle

    === Private Attributes ===
    - _attack_counter: The counter for basic attack cooldown
    """
    attack_range: int
    attack_speed: float
    attack_texture: dict[str, pygame.Surface]
    target: MultiObjectsEvaluator
    animations: dict[str, Puppet]
    speed: float

    def __init__(self, info: dict[str, Union[str, float, int]]) -> None:
        attr = ['attack_speed', 'attack_range', 'target', 'speed']
        default = {
            'attack_speed': DEFAULT_ATTACK_SPEED,
            'attack_range': DEFAULT_ATTACK_RANGE,
            'target': MultiObjectsEvaluator(DEFAULT_TARGET),
            'speed': DEFAULT_SPEED
        }
        for key in default:
            if key not in info:
                info[key] = default[key]
        for a in attr:
            setattr(self, a, info[a])
        super().__init__(info)

        optional = {
            'basic_attack_texture': BASIC_ATTACK_TEXTURE,
            'guard_texture': BASIC_ATTACK_TEXTURE
        }
        for op in optional:
            if op not in info:
                info[op] = optional[op]
        self._attack_counter = 0
        self.animations = {}

        # add moves
        basic_attack = {
            'name': 'basic_attack',
            'stamina_cost': DEFAULT_ATTACK_STAMINA_COST,
            'mana_cost': DEFAULT_ATTACK_MANA_COST,
            'cooldown': 0,
            'priority': ATTACK_PRIORITY,
            'texture': info['basic_attack_texture'],
            'time': DEFAULT_ACTION_TIMER,
            'method': self.basic_attack
        }
        move = {
            'name': 'move',
            'stamina_cost': 0,
            'mana_cost': 0,
            'cooldown': 0,
            'priority': MOVE_PRIORITY,
            'time': DEFAULT_ACTION_TIMER,
            'method': self.move
        }
        guard = {
            "name": 'guard',
            'stamina_cost': 0,
            'mana_cost': 0,
            'cooldown': GUARD_COOLDOWN,
            'priority': DEFENSE_PRIORITY,
            'time': GUARD_DURATION,
            'method': self.guard,
            'texture': GUARD_TEXTURE,
            'extendable': True
        }
        speed_up = {
            'name': "speed_up",
            'stamina_cost': round(40 / FPS, 2),
            'mana_cost': 0,
            'cooldown': 3,
            'priority': BUFF_PRIORITY,
            'time': 2,
            'method': self.speed_up,
            'extendable': True,
            'consumption': True
        }

        moves = [basic_attack, move, guard, speed_up]
        for move in moves:
            self.add_action(move)

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

    def basic_attack(self) -> bool:
        """ Damage every nearby creatures within the attack range """
        diameter = self.get_stat('diameter')
        attack_range = self.get_stat('attack_range')
        offset = diameter / 2 - attack_range
        cx = self.x + offset
        cy = self.y + offset
        info = {
            'diameter': attack_range * 2,
            'shape': self.shape,
            'texture': self.actions['basic_attack'].action_texture,
            'owner': self,
            'light_source': BASIC_ATTACK_BRIGHTNESS,
            'x': cx,
            'y': cy,
            'solid': False,
            'map_name': self.map_name,
            'sync_offset': (offset, offset),
            'update_priority': BASIC_ATTACK_TEXTURE_PRIORITY
        }
        collision_box = Puppet(info)
        self.animations["basic_attack"] = collision_box
        living = list(filter(lambda c: isinstance(Particle.particle_group[c],
                                                  Living),
                             get_nearby_particles(collision_box)))
        for entity in living:
            entity = Particle.particle_group[entity]
            if self.is_target(entity) and \
                    collision_box.detect_collision(entity):
                entity.register_damage(self.get_stat('attack_power'))
        self._attack_counter = 0
        return True

    def speed_up(self):
        self.add_stats({'speed': 100})

    def move(self, direction: Union[float, Positional]) -> None:
        if isinstance(direction, Positional):
            direction = get_direction((self.x, self.y), (direction.x,
                                                         direction.y))
        direction = math.radians(direction)
        speed = round(self.get_stat('speed') / FPS, 2)
        self.add_stats(
            {'vx': round(speed * round(math.cos(direction), 2), 2)})
        self.add_stats(
            {'vy': round(- speed * round(math.sin(direction), 2), 2)})

    def guard(self):
        if "guard" not in self.animations:
            diameter = self.get_stat('diameter')
            info = {
                'diameter': diameter * 2,
                'shape': self.shape,
                'texture': self.actions['guard'].action_texture,
                'owner': self,
                'light_source': 0,
                'x': self.x - diameter / 2,
                'y': self.y - diameter / 2,
                'solid': False,
                'map_name': self.map_name,
                'self_destroy': 3,
                'sync_offset': (-diameter / 2, -diameter / 2),
                'update_priority': 1
            }
            self.animations['guard'] = Puppet(info)
        else:
            self.animations['guard'].delay_destruction(1)
        self.add_stats({"stamina_regen": -15})
        damage = self.get_stat("incoming_damage")
        if damage > 0:
            damage = damage * self.get_stat("defense") / 100
            self.add_stats({"incoming_damage": -damage})
            self.stamina -= damage
            if self.stamina < 0:
                self.stamina = 0
                self.action_halt('guard')

    def update_status(self):
        """ This method must be called every frame to fully delete
        self-destroyed puppets
        """
        for particle in self.animations.copy():
            p = self.animations[particle]
            if p.id not in Particle.particle_group:
                self.animations.pop(particle, None)
        super().update_status()

    def is_target(self, particle: Particle) -> bool:
        contract = {
            SELF_PREFIX: self,
            OTHER_PREFIX: particle
        }
        return self.target.eval(contract)


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
    ignore: MultiObjectsEvaluator

    def __init__(self, info: dict[str, Union[str, float, int, Tuple, List]]) \
            -> None:
        super().__init__(info)
        attr = ['self_destruction', 'ignore']
        default = {
            'self_destruction': DEFAULT_PROJECTILE_COUNTDOWN,
            'ignore': MultiObjectsEvaluator(DEFAULT_TARGET)
        }
        for item in default:
            if item not in info:
                info[item] = default[item]
        for a in attr:
            setattr(self, a, info[a])
        self.destroyed = False
        self._self_destroy_counter = 0
        self.calculate_velocity()

    def calculate_velocity(self):
        speed = round(self.get_stat('speed') / FPS, 2)
        direction = math.radians(self.direction)
        self.vx += round(speed * round(math.cos(direction), 2), 2)
        self.vy += -round(speed * round(math.sin(direction), 2), 2)

    def count_down(self):
        self._self_destroy_counter += 1
        if self._self_destroy_counter >= self.self_destruction * FPS:
            self.destroyed = True

    def direction_increment(self, time: int, direction: str, total: float,
                            current: int) -> Tuple[float, float]:
        """ Increment the position of the particle in given direction """
        vel = 'v' + direction
        if self.destroyed:
            setattr(self, "v" + direction, 0)
            return 0, current
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
                    ps = get_particles_by_tiles(
                        self.map_name,
                        colliding_tiles_generator(self.x, self.y,
                                                  self.diameter))
                    for particle in ps:
                        particle = Particle.particle_group[particle]
                        if not self.ignore.eval(particle) and \
                                (self.is_target(particle) or particle.solid) \
                                and self.detect_collision(particle):
                            self.destroyed = True
                            setattr(self, "v" + direction, 0)
                            return 0, current
        return total, current

    def is_target(self, particle: Particle) -> bool:
        contract = {
            SELF_PREFIX: self,
            OTHER_PREFIX: particle
        }
        return isinstance(particle, Creature) and self.target.eval(contract)

    def action(self, optional=None):
        if not self.destroyed:
            self.count_down()
            self.enqueue_action("illuminate", {})
        else:
            self.basic_attack()
            self.remove()


class ProjectileThrowable(ActiveParticle, CombatStats, Manaized):
    """
    """
    target: BoolExpr
    fireball_explosion_range: int

    def __init__(self, info: dict[str, Union[str, float, int, BoolExpr]]) -> \
            None:
        attr = ['target', 'fireball_explosion_range']
        default = {
            'target': MultiObjectsEvaluator(DEFAULT_TARGET),
            "fireball_explosion_range": FIREBALL_EXPLOSION_RANGE
        }
        for key in default:
            if key not in info:
                info[key] = default[key]
        for a in attr:
            setattr(self, a, info[a])
        super().__init__(info)
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
            self.add_action(move)

    def fireball(self) -> None:
        """ Damage every nearby creatures inside the explosion range of
        the fireball
        """
        c1x = self.x - 1 + self.get_stat('diameter') / 2
        c1y = self.y - 1 + self.get_stat('diameter') / 2
        ball_size = int(self.get_stat('fireball_explosion_range'))
        c2x = c1x - ball_size // 2
        c2y = c1y - ball_size // 2
        condition = "( id = " + str(self.id) + " )"
        info = {
            'diameter': ball_size,
            'shape': self.shape,
            'ignore': ObjectAttributeEvaluator(condition),
            'light_source': FIREBALL_BRIGHTNESS,
            'texture': self.actions['fireball'].action_texture,
            'target': self.target,
            'attack_damage': self.get_stat('ability_power'),
            'attack_range': self.get_stat('fireball_explosion_range'),
            'speed': DEFAULT_PROJECTILE_SPEED,
            'direction': self.direction,
            'x': c2x,
            'y': c2y,
            'vx': self.get_stat("vx"),
            'vy': self.get_stat("vy"),
            'map_name': self.map_name,
            'basic_attack_texture': 'fireball_explosion.png'
        }
        Fireball(info)
