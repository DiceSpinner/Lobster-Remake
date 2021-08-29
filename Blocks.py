from particles import *
from utilities import Interactive
from typing import Any


class Door(Block, Interactive):
    """ A door that can be interacted with

    === Public Attributes ===
    - opened: A flag that indicates whether this door is opened or not
    """
    opened: bool
    opened_texture: str

    def __init__(self, info: dict[str, Union[str, float, int, bool]]) -> None:
        if 'opened' not in info:
            self.opened = False
        else:
            self.opened = info['opened']
        super().__init__(info)

    def upon_interact(self, other: Any) -> None:
        if self.opened:
            self.opened = False
            self.solid = True
            self.light_resistance = 256
            self.texture = 'door_1_close-brown.jpg'
        else:
            self.opened = True
            self.solid = False
            self.light_resistance = 0
            self.texture = 'door_1_open.png'

    def can_interact(self, other: Any) -> bool:
        return True
