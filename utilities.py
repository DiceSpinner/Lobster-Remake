from __future__ import annotations
from typing import Union, List, Optional, Any, Tuple
from error import UnknownShapeError
from bool_expr import BoolExpr, construct_from_list, construct_from_str
from settings import *
import math


class DynamicStats:
    """ Objects with dynamic stats.
    i.e The actual attack damage the player can deal is the sum of his
    base attack damage and attack bonus from item/effect. This can change
    dynamically when the player loses/gain item/effect.

    === Private Attributes ===
    - _buffer_stats: A collection of external applied stats
    """
    _buffer_stats: dict[str, Any]

    def __init__(self) -> None:
        """ Initialize a set of additional attributes """
        self._buffer_stats = {}

    def add_stats(self, info: dict[str, Any]) -> None:
        """ Add external stats to the buffer """
        for data in info:
            if hasattr(self, data):
                if data not in self._buffer_stats:
                    self._buffer_stats[data] = info[data]
                elif not isinstance(info[data], int) and not isinstance(
                        info[data], float):
                    self._buffer_stats[data] = info[data]
                else:
                    self._buffer_stats[data] += info[data]

    def get_stat(self, item: str) -> Any:
        if not hasattr(self, item):
            raise AttributeError
        col = vars(self)
        if item in self._buffer_stats:
            if not isinstance(col[item], int) and not isinstance(
                    col[item], float):
                return self._buffer_stats[item]
            else:
                return col[item] + self._buffer_stats[item]
        else:
            return col[item]

    def reset(self):
        self._buffer_stats = {}


class Positional:
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


class Movable(Positional, DynamicStats):
    """ An interface that provides movement methods in addition to positional
        attributes.

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
        Positional.__init__(self, info)
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

        DynamicStats.__init__(self)

    def update_position(self) -> None:
        """
        Update the object's position.
        """
        raise NotImplementedError

    def move(self, direction: Union[int, Positional]) -> None:
        """ Move towards the target direction or object """
        if isinstance(direction, Positional):
            direction = get_direction((self.x, self.y), (direction.x,
                                                         direction.y))
        direction = math.radians(direction)
        self.add_stats({'vx': self.get_stat('speed') * round(math.cos(direction), 2)})
        self.add_stats({'vy': - self.get_stat('speed') * round(math.sin(direction), 2)})


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
        Positional.__init__(self, info)
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


class Collidable(Positional, DynamicStats):
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
        Positional.__init__(self, info)
        attr = ['diameter', 'shape', 'solid']
        dynamic_stats = ['diameter', 'shape', 'solid']
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
        DynamicStats.__init__(self)

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


class Lightable(DynamicStats):
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
        DynamicStats.__init__(self)

    def enlighten(self, other: Lightable) -> None:
        """ Raise self and other lightable object's brightness """
        if self.get_stat('brightness') < self.get_stat('light_source'):
            self.add_stats({'brightness': self.get_stat('light_source') -
                            self.get_stat('brightness')})
        light_level = self.get_stat('brightness') - \
            self.get_stat('light_resistance')
        if light_level < 0:
            return
        if light_level > other.get_stat('brightness'):
            other.add_stats({'brightness': light_level -
                            other.get_stat('brightness')})


class Living(DynamicStats):
    """ Description: Interface for living objects

    === Public Attributes ===
    - health: The health of the object
    - max_health: The maximum hit points of the object
    - death: Whether this object is dead
    """
    health: float
    max_health: float
    death: BoolExpr

    def __init__(self, info: dict[str, Union[int, str, List]]) -> None:
        attr = ['health', 'max_health', 'death']
        default = {
            'health': DEFAULT_HEALTH,
            'max_health': DEFAULT_MAX_HEALTH,
            'death': construct_from_str("( not health > 0 )")
        }
        for key in default:
            if key not in info:
                info[key] = default[key]
        for a in attr:
            setattr(self, a, info[a])
        DynamicStats.__init__(self)

    def is_dead(self) -> bool:
        """ Check whether this object is dead """
        return self.get_stat('death').eval(vars(self))

    def die(self):
        raise NotImplementedError


class Attackable(DynamicStats):
    """ Attacking Interface that provides offensive movements

    === Public Attributes ===
    - attack_power: The strength of the attack
    - attack_speed: Number of frames between each attacks
    - attack_range: The range of the attack

    === Private Attributes ===
    - attack_counter: Time counter for attacks
    """

    attack_power: float
    attack_speed: int
    attack_range: int
    _attack_counter: int

    def __init__(self, info: dict[str, Union[int, float]]) -> None:
        self._attack_counter = 0
        attr = ['attack_power', 'attack_speed', 'attack_range']
        default = {
            'attack_power': DEFAULT_ATTACK_DAMAGE,
            'attack_speed': DEFAULT_ATTACK_SPEED,
            'attack_range': DEFAULT_ATTACK_RANGE,
            '_attack_counter': 0
        }
        for key in default:
            if key not in info:
                info[key] = default[key]
        for a in attr:
            setattr(self, a, info[a])
        DynamicStats.__init__(self)

    def count(self) -> None:
        """ Increase the attack counter by 1 each frame. """
        if self._attack_counter < self.attack_speed:
            self._attack_counter += 1

    def can_attack(self) -> bool:
        return self._attack_counter >= self.attack_speed

    def attack(self, targets: Optional[List[Living]]) -> None:
        """ Perform an attack and reset the attack counter """
        raise NotImplementedError


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
    else:
        if obj1[1] < obj2[1]:
            value = arctan
        else:
            value = arctan + 180
    if value >= 360:
        value = value % 360
    elif value < 0:
        while value < 0:
            value += 360
    return round(value, 2)
