from __future__ import annotations
from typing import Union, List
from error import UnknownShapeError
from bool_expr import BoolExpr, construct_from_list
import math


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

    def __init__(self, info: dict[str, Union[str, float]]) -> None:
        attr = ['x', 'y', 'map_name']
        for item in attr:
            if item not in info:
                info[item] = 0
        for item in info:
            if item in attr:
                setattr(self, item, info[item])


class Movable(Positional):
    """ An interface that provides movement methods in addition to positional
        attributes.

    === Public Attributes ===
    - vx: Velocity of the object in x-direction
    - vy: Velocity of the object in y-direction
    """

    vx: float
    vy: float

    def __init__(self, info: dict[str, Union[str, float]]) -> None:
        Positional.__init__(self, info)
        attr = ['vx', 'vy', 'ax', 'ay']
        default = ['vx', 'vy', 'ax', 'ay']
        for key in default:
            if key not in info:
                info[key] = 0

        for item in info:
            if item in attr:
                setattr(self, item, info[item])

    def update_position(self) -> None:
        """
        Update the object's position.
        """
        self.x += self.vx
        self.y += self.vy


class Directional:
    """

    """
    pass


class Collidable(Positional):
    """ Description: Collision interface supports square and circle
    shaped objects

    === Public Attributes ===
    - diameter: collision diameter of the object
    - shape: shape of the object
    """
    diameter: int
    shape: str

    def __init__(self, info: dict[str, Union[int, str]]) -> None:
        Positional.__init__(self, info)
        attr = ['diameter', 'shape']
        default = {
            'diameter': 30,
            'shape': 'square'
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
        if self.x < other.x - self.diameter:
            return False
        if self.y < other.y - self.diameter:
            return False
        if self.x - other.diameter > other.x:
            return False
        if self.y - other.diameter > other.y:
            return False
        return True

    def _square_circle(self, other: Collidable) -> bool:
        radius = other.diameter / 2
        cx = other.x + radius
        cy = other.y + radius

        if self.x > cx:
            if self.y > cy:
                return math.sqrt(pow(self.x - cx, 2) +
                                 pow(self.y - cy, 2)) < radius
            elif self.y + self.diameter < cy:
                return math.sqrt(pow(self.x - cx, 2) +
                                 pow(self.y + self.diameter - cy, 2)) <= radius
        elif self.x + self.diameter < cx:
            if self.y > cy:
                return math.sqrt(pow(self.x + self.diameter - cx, 2) +
                                 pow(self.y - cy, 2)) < radius
            elif self.y + self.diameter < cy:
                return math.sqrt(pow(self.x + self.diameter - cx, 2) +
                                 pow(self.y + self.diameter - cy, 2)) < radius
        return self._square_square(other)

    def _circle_circle(self, other: Collidable) -> bool:
        r1 = self.diameter / 2
        cx1 = self.x + r1
        cy1 = self.y + r1

        r2 = other.diameter / 2
        cx2 = other.x + r2
        cy2 = other.y + r2

        return math.sqrt(pow(cx1 - cx2, 2) + pow(cy1 - cy2, 2)) < (r1 + r2)

    def _circle_square(self, other: Collidable) -> bool:
        return other._square_circle(self)


class Lightable:
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
        attr = ['brightness', 'light_source']
        default = {
            'brightness': 100,
            'light_source': 100,
            'light_resistance': 10
        }
        for key in default:
            if key not in info:
                info[key] = default[key]
        for a in attr:
            setattr(self, a, info[a])

    def enlighten(self, other: Lightable) -> None:
        """ Raise self and other lightbale object's brightness """
        if self.brightness < self.light_source:
            self.brightness = self.light_source
        light_level = self.brightness - other.light_resistance
        if light_level > other.brightness:
            other.brightness = light_level

    def reset(self):
        """ Reset the brightness, this method should be called on each lightable
        object once per frame
         """
        self.brightness = 0


class Living:
    """ Description: Interface for living objects

    === Public Attributes ===
    - health: The health of the object
    - death: Whether this object is dead
    """
    health: float
    death: BoolExpr

    def __init__(self, info: dict[str, Union[int, str, List]]) -> None:
        attr = ['brightness', 'light_source']
        default = {
            'health': 100,
            'death': [[('health', '< 1')]]
        }
        for key in default:
            if key not in info:
                info[key] = default[key]
        setattr(self, 'health', info['health'])
        self.death = construct_from_list(info['death'])

    def is_dead(self) -> bool:
        """ Check whether this object is dead """
        raise NotImplementedError

    def update_status(self) -> None:
        """ Update the status of the object """
        raise NotImplementedError
