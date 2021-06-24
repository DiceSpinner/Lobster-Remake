from typing import Union


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

    def update(self) -> None:
        """
        Update the object's position.
        """
        self.x += self.vx
        self.y += self.vy
