from __future__ import annotations
from typing import Union, List, Tuple
from settings import *
import pygame
import public_namespace


class Item:
    """ A item in game

    === Public Attributes ===
    - name: Name of this item
    - image: The image of this item
    - description: Description of this item
    - max_stack: The maximum amount of stacks this item can have
    - stack: The current stack of this item
    - shape: Shape of this item
    - diameter: Diameter of this item

    === Representation Invariant ===
    - max_stack >= 1
    - stack >= 1
    """
    name: str
    description: str
    max_stack: int
    stack: int
    image: str
    shape: str
    diameter: int

    def __init__(self, info: dict[str, Union[int, str, List]]) -> None:
        attr = ['name', 'description', 'max_stack', 'stack', 'image',
                'diameter', 'shape']
        default = {}
        for key in default:
            if key not in info:
                info[key] = default[key]
        for a in attr:
            setattr(self, a, info[a])

    def __eq__(self, other: Item) -> bool:
        """ Two items are considered the same if they share the same name """
        assert isinstance(other, Item)
        return self.name == other.name

    def merge(self, other: Item) -> None:
        """ Merge stacks of the items

        Pre-condition: self == other
        """
        self.stack += other.stack
        if self.stack >= self.max_stack:
            other.stack = self.stack - self.max_stack
            self.stack = self.max_stack
        else:
            other.stack = 0

    def display(self, screen: pygame.Surface,
                location: Tuple[int, int], size: Tuple[int, int],
                description: bool) -> None:
        texture = public_namespace.get_texture_by_info(
            self.image, size, 0, 255)
        if description:
            font = pygame.font.Font(None, 25)
            text = font.render(self.description, True, (0, 255, 0))
            screen.blit(text, (location[0] + ITEM_IMAGE_SIZE + 10, location[1]))
            s = str(self.stack) + " / " + str(self.max_stack)
            stack = font.render(s, True, (0, 255, 0))
            screen.blit(stack, (location[0] + ITEM_IMAGE_SIZE + 10,
                                location[1] + 20))
        screen.blit(texture, location)


class Inventory:
    """ Inventory used to store items

    === Public Attributes ===
    - size: Size of this inventory
    - items: Items stored in this inventory

    === Representation Invariant ===
    - size >= 0
    """
    size: int
    items: List[Item]

    def __init__(self, info: dict[str, Union[int, str, List, Item]]) -> None:
        self.size = info['size']
        try:
            self.items = [info['one_item']]
        except KeyError:
            self.items = []

    def add(self, item: Item) -> None:
        """ Add items to this inventory """
        same_items = []
        for i in self.items:
            if i == item:
                same_items.append(i)
        for i in same_items:
            i.merge(item)
            if item.stack == 0:
                return
        if len(self.items) < self.size:
            self.items.append(item)
