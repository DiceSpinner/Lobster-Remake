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
    closed_texture: str

    def __init__(self, info: dict[str, Any]) -> None:
        default = {
            'opened': False
        }
        attr = ['opened', 'opened_texture', 'closed_texture']
        for key in default:
            if key not in info:
                info[key] = default[key]
        for item in attr:
            setattr(self, item, info[item])
        super().__init__(info)

    def upon_interact(self, other: Any) -> None:
        if self.opened:
            self.opened = False
            self.solid = True
            self.light_resistance = 256
            self.texture = self.closed_texture
        else:
            self.opened = True
            self.solid = False
            self.light_resistance = 0
            self.texture = self.opened_texture

    def can_interact(self, other: Any) -> bool:
        return True
