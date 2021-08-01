from __future__ import annotations
from typing import Union, List, Optional, Any, Tuple, Callable
from error import UnknownShapeError, InvalidAttrTypeError
from bool_expr import BoolExpr, construct_from_list, construct_from_str
from settings import *
from data_structures import WeightedPriorityQueue
import math


def compare_by_execution_priority(i1: Tuple[Staminaized, dict[str, Any], str],
                                  i2: Tuple[Staminaized, dict[str, Any], str])\
        -> bool:
    """ Sort by non-decreasing order """
    a1 = i1[0].actions[i1[2]]
    a2 = i2[0].actions[i2[2]]
    return a1.action_priority < a2.action_priority


class BufferedStats:
    """ Objects with buffered stats.
    i.e The actual attack damage the player can deal is the sum of his
    base attack damage and attack bonus from item/effect. This can change
    dynamically when the player loses/gain item/effect.

    === Private Attributes ===
    - _buffer_stats: A collection of external applied stats
    """
    _buffer_stats: dict[str, Any]

    def __init__(self, place_holder: Optional[Any]) -> None:
        """ Initialize a set of additional attributes """
        self._buffer_stats = {}

    def add_stats(self, info: dict[str, Any]) -> None:
        """ Add external stats to the buffer """
        for data in info:
            if hasattr(self, data):
                if data not in self._buffer_stats:
                    self._buffer_stats[data] = info[data]
                elif isinstance(self._buffer_stats[data], dict) and \
                        isinstance(info[data], dict):
                    dict_merge(self._buffer_stats[data], info[data])
                elif isinstance(self._buffer_stats[data], str) and \
                        isinstance(info[data], str):
                    self._buffer_stats[data] = info[data]
                elif (isinstance(self._buffer_stats[data], int) or
                      isinstance(self._buffer_stats[data], float)) and \
                        (isinstance(info[data], int) or isinstance(info[data],
                                                                   float)):
                    self._buffer_stats[data] += info[data]
                else:
                    raise InvalidAttrTypeError

    def get_stat(self, item: str) -> Any:
        v1 = getattr(self, item)
        try:
            v2 = self._buffer_stats[item]
            f2 = isinstance(v2, int) or isinstance(v2, float)
            if not f2:
                return v2
            return v1 + v2
        except KeyError:
            return v1

    def reset(self):
        self._buffer_stats = {}


class Positional(BufferedStats):
    """ An interface that provides positional attributes

    === Public Attributes ===
    - map_name: name of the map the object is in
    - x: x-coordinate of the object
    - y: y-coordinate of the object
    """
    map_name: str
    x: float
    y: float

    def __init__(self, info: dict[str, Union[str, int]]) -> None:
        attr = ['x', 'y', 'map_name']
        for item in attr:
            if item not in info:
                info[item] = 0
        for item in info:
            if item in attr:
                setattr(self, item, info[item])
        super().__init__(info)


class Movable(BufferedStats):
    """ An interface that provides movement attributes.

    === Public Attributes ===
    - vx: Velocity of the object in x-direction
    - vy: Velocity of the object in y-direction
    - ax: Acceleration of the object in x-direction
    - ay: Acceleration of the object in y-direction
    - dynamic stats
    """
    vx: float
    vy: float
    ax: float
    ay: float
    speed: float

    def __init__(self, info: dict[str, Union[str, float]]) -> None:
        super().__init__(info)
        attr = ['vx', 'vy', 'ax', 'ay', 'speed']
        default = {
            'vx': 0,
            'vy': 0,
            'ax': 0,
            'ay': 0,
            'speed': 2
        }
        for key in default:
            if key not in info:
                info[key] = default[key]

        for item in info:
            if item in attr:
                setattr(self, item, info[item])


class Directional(Positional):
    """ Interface for directional objects

    === Public Attributes ===
    - direction: Direction of the object in degrees. direction = 0 when the
        unit is facing right (3 o'clock, going counter clockwise as the
        degree increases)

    === Representation Invariants ===
    - 0 <= direction < 360
    """

    direction: float

    def __init__(self, info: dict[str, Union[str, float]]) -> None:
        super().__init__(info)
        attr = ['direction']
        default = {
            'direction': 0
        }

        for key in default:
            if key not in info:
                info[key] = default[key]

        for item in info:
            if item in attr:
                setattr(self, item, info[item])

    def aim(self, obj: Positional) -> None:
        """ Change the direction pointing to the obj """
        direction = get_direction((self.x, self.y), (obj.x, obj.y))
        self.direction = direction


class Collidable(Positional, BufferedStats):
    """ Description: Collision interface supports square and circle
    shaped objects

    === Public Attributes ===
    - diameter: collision diameter of the object
    - shape: shape of the object
    - solid: whether this object can be passed through by other objects
    """

    diameter: int
    shape: str
    solid: bool

    def __init__(self, info: dict[str, Union[int, str]]) -> None:
        super().__init__(info)
        attr = ['diameter', 'shape', 'solid']
        default = {
            'diameter': 30,
            'shape': 'square',
            'solid': False
        }

        for key in default:
            if key not in info:
                info[key] = default[key]
        for a in attr:
            setattr(self, a, info[a])

    def detect_collision(self, other: Collidable) -> bool:
        if other.diameter == 0 or self.diameter == 0:
            return False
        if self.shape == 'square':
            if other.shape == 'square':
                return self._square_square(other)
            elif other.shape == 'circle':
                return self._square_circle(other)
            else:
                raise UnknownShapeError
        elif self.shape == 'circle':
            if other.shape == 'square':
                return self._circle_square(other)
            elif other.shape == 'circle':
                return self._circle_circle(other)
            else:
                raise UnknownShapeError
        else:
            raise UnknownShapeError

    def _square_square(self, other: Collidable) -> bool:
        """ Collision Detection between two squares """
        c1x = round(self.x, 0)
        c1y = round(self.y, 0)
        c2x = round(other.x, 0)
        c2y = round(other.y, 0)
        if c1x <= c2x - self.diameter:
            return False
        if c1y <= c2y - self.diameter:
            return False
        if c1x - other.diameter + 1 >= c2x:
            return False
        if c1y - other.diameter + 1 >= c2y:
            return False
        return True

    def _square_circle(self, other: Collidable) -> bool:
        radius = other.diameter / 2
        c1x = round(self.x, 0)
        c1y = round(self.y, 0)
        c2x = round(other.x, 0) + radius - 1
        c2y = round(other.y, 0) + radius - 1

        if c1x > c2x:
            if c1y > c2y:
                return math.sqrt(pow(c1x - c2x, 2) +
                                 pow(c1y - c2y, 2)) < radius
            elif c1y + self.diameter - 1 < c2y:
                return math.sqrt(pow(c1x - c2x, 2) +
                                 pow(c1y + self.diameter - 1 - c2y, 2)) \
                       < radius
        elif c1x + self.diameter - 1 < c2x:
            if c1y > c2y:
                return math.sqrt(pow(c1x + self.diameter - 1 - c2x, 2) +
                                 pow(c1y - c2y, 2)) < radius
            elif c1y + self.diameter - 1 < c2y:
                return math.sqrt(pow(c1x + self.diameter - 1 - c2x, 2) +
                                 pow(c1y + self.diameter - 1 - c2y, 2)) \
                       < radius
        return self._square_square(other)

    def _circle_circle(self, other: Collidable) -> bool:
        r1 = self.diameter / 2
        cx1 = self.x + r1 - 1
        cy1 = self.y + r1 - 1

        r2 = other.diameter / 2
        cx2 = other.x + r2 - 1
        cy2 = other.y + r2 - 1
        return math.sqrt(pow(cx1 - cx2, 2) + pow(cy1 - cy2, 2)) < (r1 + r2)

    def _circle_square(self, other: Collidable) -> bool:
        return other._square_circle(self)


class Lightable(BufferedStats):
    """ Description: Light interface

    === Public Attributes ===
    - brightness: The brightness of this object
    - light_source: The ability of this object to produce light
    - light_resistance: The ability of this object to block light,
        does not block self-emitted light

    Representation Invariants:
        0<= light_source <= 255
        0<= brightness <= 255
    """
    brightness: int
    light_source: int
    light_resistance: int

    def __init__(self, info: dict[str, Union[int, str]]) -> None:
        attr = ['brightness', 'light_source', 'light_resistance']
        default = {
            'brightness': 0,
            'light_source': 0,
            'light_resistance': 10
        }
        for key in default:
            if key not in info:
                info[key] = default[key]
        for a in attr:
            setattr(self, a, info[a])
        super().__init__(info)


class Regenable(BufferedStats):
    """ Description: Interface that provides access to resource regeneration

    === Public Attributes ===
    - regen_stats: A collection of stats that can be regenerated
    - stats_max: The maximum value the stats can be regenerated to
    - max stats in stats_max
    - regen stats in regen_stats

    === Representation Invariants ===
    - Regeneration can only be applied to numeric attributes
    - Values in regen_stats must be numeric
    - Regeneration is directly applied to the base stat
    - regen_stats can contain negative values, which results in stats depletion
    """
    regen_stats: List[str]
    stats_max: List[str]

    def __init__(self, info: dict[str, Union[int, float, str, List]]) -> None:
        super().__init__(info)
        self.regen_stats = []
        self.stats_max = []
        for item in info:
            # contracted naming  i.e 'max_health' stands for the threshold for
            # health attribute
            if "max_" in item:
                self.stats_max.append(item)
            elif '_regen' in item:
                attr = item[0:-6]
                self.regen_stats.append(attr)
                setattr(self, item, info[item])

    def regen(self) -> None:
        """ Regenerate stats, this method should be called every frame """
        for r in self.regen_stats:
            if hasattr(self, r):
                value = round(self.get_stat(r + "_regen") / FPS, 2)
                result = value + getattr(self, r)
                max_stat = "max_" + r
                if max_stat in self.stats_max:
                    max_value = self.get_stat(max_stat)
                    if result > max_value:
                        setattr(self, r, max_value)
                    else:
                        setattr(self, r, result)
                else:
                    setattr(self, r, result)
            else:
                self.regen_stats.remove(r)


class Living(Regenable):
    """ Description: Interface for living objects

    === Public Attributes ===
    - health: The health of the object
    - max_health: The maximum hit points of the object
    - death: Whether this object is dead
    - incoming_damage: The amount of damage this unit will take during the
        current frame
    - incoming_healing: The amount of healing this unit will receive during the
        current frame
    """
    health: float
    max_health: float
    death: BoolExpr
    incoming_damage: float
    incoming_healing: float

    def __init__(self, info: dict[str, Union[int, str, List]]) -> None:
        attr = ['health', 'max_health', 'death', 'incoming_damage',
                'incoming_healing']
        default = {
            'health': DEFAULT_HEALTH,
            'health_regen': DEFAULT_HEALTH_REGEN,
            'max_health': DEFAULT_MAX_HEALTH,
            'death': construct_from_str("( not health > 0 )"),
            'incoming_damage': 0,
            'incoming_healing': 0
        }
        for key in default:
            if key not in info:
                info[key] = default[key]
        for a in attr:
            setattr(self, a, info[a])
        super().__init__(info)

    def calculate_health(self) -> None:
        """ Update health with value changes in the buffer """
        heal = self.get_stat("incoming_healing")
        damage = self.get_stat("incoming_damage")
        if heal > 0:
            self.health += heal
        if damage > 0:
            self.health -= damage

    def register_damage(self, damage: float) -> None:
        self.add_stats({"incoming_damage": damage})

    def register_healing(self, healing: float) -> None:
        self.add_stats({"incoming_healing": healing})

    def is_dead(self) -> bool:
        """ Check whether this object is dead """
        return self.get_stat('death').eval(vars(self))

    def die(self):
        raise NotImplementedError


class Action:
    """ An action that particles can perform

    === Public Attributes ===
    - name: Name of this action
    - stamina_cost: Stamina cost of this action
    - mana_cost: Mana cost of this action
    - cooldown: Cooldown of this action
    - time: The amount of frames this action is going to last
    - action_priority: The execution priority of this action
    - action_texture: Names of assets of Visual Displays of this action
    - executing: Timer for this action while executing.

    === Private Attributes ===
    - _cooldown_counter: The counter of the cooldown
    """
    name: str
    cooldown: float
    action_time: int
    action_priority: int
    action_texture: str
    _cooldown_counter: int
    method: Callable
    executing: int

    def __init__(self, info: dict[str, Any]) -> None:
        self.name = info['name']
        self.cooldown = info['cooldown']
        self._cooldown_counter = self.cooldown * FPS
        self.action_priority = info['priority']
        self.action_time = math.ceil(info['time'])
        self.method = info['method']
        self.executing = 0
        if 'texture' in info:
            self.action_texture = info['texture']

    def can_act(self) -> bool:
        if self.executing == 0:
            # Check if the action is on cooldown
            if self._cooldown_counter < self.cooldown * FPS:
                return False
            return True
        return False

    def count(self):
        if self._cooldown_counter < self.cooldown * FPS:
            self._cooldown_counter += 1

    def execute(self, args: dict[str, Any]):
        self.method(**args)
        self._cooldown_counter = 0
        self.executing -= 1


class Staminaized(Regenable):
    """ Interface that provides access to actions

    === Public Attributes ===
    - stamina: The required stats to perform actions
    - max_stamina: The maximum amount of stamina this unit can have
    - actions: All actions this unit can perform
    """

    action_queue = WeightedPriorityQueue(compare_by_execution_priority)
    stamina: float
    max_stamina: float
    actions: dict[str, Action]
    stamina_costs: dict[str, float]

    def __init__(self, info: dict[str, Union[int, str, List]]) -> None:
        attr = ['stamina', 'max_stamina']
        default = {
            'stamina': DEFAULT_STAMINA,
            'max_stamina': DEFAULT_MAX_STAMINA,
            'stamina_regen': DEFAULT_STAMINA_REGEN
        }
        self.actions = {}
        self.stamina_costs = {}
        for key in default:
            if key not in info:
                info[key] = default[key]
        for a in attr:
            setattr(self, a, info[a])
        super().__init__(info)

    def can_act(self, name: str) -> bool:
        """ Return whether the given action can be performed """
        action = self.actions[name]
        if action.can_act():
            # Stamina check
            return self.stamina >= self.stamina_costs[name]
        return False

    def cooldown_countdown(self) -> None:
        """ Increase the cooldown counter of actions by 1 per frame. """
        for name in self.actions:
            self.actions[name].count()

    def enqueue_movement(self, name: str, args: dict[str, Any]) -> None:
        """ Add the action to the action queue """
        if self.can_act(name):
            Staminaized.action_queue.enqueue((self, args, name),
                                             self.actions[name].action_time)
            self.actions[name].executing = self.actions[name].action_time
            self.resource_consume(name)

    def execute_movement(self, name: str, args: dict[str, Any]):
        """ Execute movements in self.executing """
        self.actions[name].execute(args)

    def resource_consume(self, name: str):
        """ Consume the resource for performing this action """
        self.stamina -= self.stamina_costs[name]

    def add_movement(self, info: dict[str, Union[str, float, int]]) -> None:
        """ Add movement methods to this object

        Pre-condition: info contains all of the following
            1. name of the action accessed by "name"
            2. stamina cost of the action accessed by "stamina_cost"
            3. cooldown of the action accessed by "cooldown"
            4. Length of the action accessed by "time"
            5. Execution priority of this action accessed by "priority"
            6. method reference of this action accessed by "method"

        Optional:
            1. Texture of the action accessed by "texture"
        """
        name = info['name']
        act = Action(info)
        self.stamina_costs[name] = info['stamina_cost']
        self.actions[name] = act
        if 'texture' in info:
            self.actions[name].action_texture = info['texture']


class Manaized(Staminaized):
    """ Interface that provides access to movements that depletes resource bar

    === Public Attributes ===
    - mana: The required stats to perform manaized movements
    - max_mana: The maximum amount of mana this unit can have
    - mana_costs: The mana costs of all actions
    """
    mana: float
    max_mana: float
    mana_costs: dict[str, float]

    def __init__(self, info: dict[str, Union[int, str, List]]) -> None:
        attr = ['mana', 'max_mana']
        default = {
            'mana': DEFAULT_MANA,
            'max_mana': DEFAULT_MAX_MANA,
            'mana_regen': DEFAULT_MANA_REGEN
        }
        for key in default:
            if key not in info:
                info[key] = default[key]
        for a in attr:
            setattr(self, a, info[a])
        self.mana_costs = {}
        super().__init__(info)

    def can_act(self, name: str) -> bool:
        """ Return whether the given action can be performed """
        if Staminaized.can_act(self, name):
            return self.mana >= self.mana_costs[name]
        return False

    def resource_consume(self, name: str):
        """ Consume the resource for performing this action """
        Staminaized.resource_consume(self, name)
        self.mana -= self.mana_costs[name]

    def add_movement(self, info: dict[str, Union[str, float, int]]) -> None:
        """ Add movement methods to this object

        Pre-condition: info contains all of the following
            1. name of the action accessed by "name"
            2. stamina cost of the action accessed by "stamina_cost"
            3. cooldown of the action accessed by "cooldown"
            4. Length of the action accessed by "time"
            5. Execution priority of this action accessed by "priority"
            6. mana cost of the action accessed by "mana_cost"
            7. method reference of this action accessed by "method"

        Optional:
            1. Texture of the action accessed by "texture"
        """
        self.mana_costs[info['name']] = info['mana_cost']
        Staminaized.add_movement(self, info)


class CombatStats:
    """ Interface that provides offensive stats

    === Public Attributes ===
    - attack_power: The strength of the attack
    - ability_power: Scaling factor for ability strength
    - defense: Scaling factor for defense effectiveness
    - active_damage_reduction: Damage reduction for this unit in guarded stance
    """

    attack_power: float
    ability_power: float
    defense: float
    active_damage_reduction: float

    def __init__(self, info: dict[str, Union[int, float]]) -> None:
        self._attack_counter = 0
        attr = ['attack_power', 'ability_power']
        default = {
            'attack_power': DEFAULT_ATTACK_DAMAGE,
            'ability_power': DEFAULT_ABILITY_POWER
        }
        for key in default:
            if key not in info:
                info[key] = default[key]
        for a in attr:
            setattr(self, a, info[a])
        super().__init__(info)


def get_direction(obj1: Tuple[float, float], obj2: Tuple[float, float]) \
        -> float:
    """ Get direction of the obj2 from obj1

    >>> p1 = (0, 0)
    >>> p2 = (5, 5)
    >>> get_direction(p1, p2)
    315.0
    >>> p3 = (2, 3)
    >>> get_direction(p1, p3)
    303.69
    >>> get_direction(p2, p3)
    326.31
    """
    x_dif = obj2[0] - obj1[0]
    # Reversed y-axis on screen
    y_dif = obj1[1] - obj2[1]
    if x_dif == 0:
        if obj1[1] < obj2[1]:
            return 270
        else:
            return 90
    tan = y_dif / x_dif
    arctan = math.degrees(math.atan(tan))
    if tan > 0:
        if obj1[1] < obj2[1]:
            value = 180 + arctan
        else:
            value = arctan
    elif tan < 0:
        if obj1[1] < obj2[1]:
            value = arctan
        else:
            value = arctan + 180
    elif x_dif > 0:
        value = 0
    else:
        value = 180
    if value >= 360:
        value = value % 360
    elif value < 0:
        while value < 0:
            value += 360
    return round(value, 1)


def dict_merge(d1: dict[str, Any], d2: dict[str, Any]):
    """ Import stats from d2 and merge them inside d1 """
    for item in d2:
        if item not in d1:
            d1[item] = d2[item]
            continue
        if isinstance(d2[item], int) or isinstance(d2[item], float):
            if isinstance(d1[item], int) or isinstance(d1[item], float):
                d1[item] += d2[item]
                continue
            raise InvalidAttrTypeError
