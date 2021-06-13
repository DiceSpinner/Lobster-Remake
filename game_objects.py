import pygame
from typing import List, Any, Tuple, Union

IMAGE_SIZE = 65  # Must be an odd number


class Particle(pygame.sprite.Sprite):
    """
    Description: Customized sprites

    === Public Attributes ===
    pos: A dictionary that stores the position of this particle in the map,
        the key is the name of the map and the values are x-y coordinates.

    attributes: A dictionary that stores attributes of this particle
    texture: Texture of this particle
    """
    pos: dict[str, Union[str, float]]
    attributes: dict[str, Any]
    texture: pygame.Surface

    def __init__(self, m: str, x: float, y: float) -> None:
        pygame.sprite.Sprite.__init__(self)
        self.attributes = {}
        self.pos = {
            'map_name': m,
            'x': x,
            'y': y
        }

    def display(self, screen: pygame.Surface):
        raise NotImplementedError


class Entity(Particle):
    """
    Description: Customized particles

    Additional Attributes:
        shape: (str) Shape of this entity
        radius: (str) Physics radius of this entity
        light_source: Whether this entity is a light source or not
        brightness: Current brightness of this entity
        light_power: The ability of this entity to produce light

    Representation Invariants:
        radius >= 0
        shape is one of 'circle', 'rect', 'tri'
        0<= light_power <= 255 and can only be 0 when this entity is
            not a light source
        0<= brightness <= 255
    """

    def __init__(self, radius: float, shape: str, m: str,
                 x: float, y: float, light_source: bool,
                 light_power: int) -> None:
        Particle.__init__(self, m, x, y)
        self.attributes['shape'] = shape
        self.attributes['radius'] = radius
        self.attributes['brightness'] = 0
        self.attributes['light_source'] = light_source
        self.attributes['light_power'] = light_power

    def display(self, screen: pygame.Surface):
        raise NotImplementedError


class Creature(Entity):
    """
    Description: Customized entities

    Additional Attributes:
        shape: (str) Shape of this entity
        radius: (str) Physics radius of this entity
        light_source: Whether this entity is a light source or not
        brightness: Current brightness of this entity
        light_power: The ability of this entity to produce light

    Representation Invariants:
        radius >= 0
        shape is one of 'circle', 'rect'
        0<= light_power <= 255 and can only be 0 when this entity is
            not a light source
        0<= brightness <= 255
    """

    def __init__(self, radius: float, shape: str, m: str,
                 x: float, y: float, light_source: bool, light_power: int,
                 health: float, speed: float) -> None:
        Entity.__init__(self, radius, shape, m, x, y, light_source, light_power)
        self.attributes['health'] = health
        self.attributes['speed'] = speed

    def display(self, screen: pygame.Surface) -> None:
        screen.blit(self.texture, [self.pos['x'] - IMAGE_SIZE // 2,
                                   self.pos['y'] - IMAGE_SIZE // 2])


class Block(Entity):
    """

    """

    def display(self, screen: pygame.Surface) -> None:
        screen.blit(self.texture, [self.pos['x'] - IMAGE_SIZE // 2,
                                   self.pos['y'] - IMAGE_SIZE // 2])
        dark = pygame.Surface((self.attributes['radius'],
                               self.attributes['radius']))
        dark.set_alpha(255 - self.attributes['brightness'])
        screen.blit(dark, [self.pos['x'] - self.attributes['radius'],
                           self.pos['y'] - self.attributes['radius']])


class GameMap:
    """
    Description: Game map object

    === Public Attributes ===
    name: name of the map
    length: length of the map (in blocks)
    width: width of the map (in blocks)
    content: content of the map
    maximum_radius: The maximum radius of all entities on this map, this
        variable will be used to implement more efficient collision detection
        method in the future.
    blocks: Pre-defined blocks for this map
    creatures: Pre-defined creatures for this map
    """
    name: str
    length: int
    width: int
    content: dict[str, Union[List[List[Block]], List[Creature]]]
    maximum_radius: int
    blocks: dict[str, Union[dict[str, Union[int, float, str]],
                            Union[int, float, str]]]
    creatures: dict[str, Union[dict[str, Union[int, float, str]],
                               Union[int, float, str]]]

    def __init__(self, name: str, content: str, blocks: str, creatures: str,
                 width: int, length: int) -> None:
        self.name = name
        self.width = width
        self.length = length
        self.content = {
            'block': [],
            'creature': []
        }
        self.load_assets(blocks, creatures)
        self._construct_content(content)

    def load_assets(self, blocks: str, creatures: str):
        """
        Load in predefined blocks and creatures for this map.
        """
        file = [blocks, creatures]
        store = [self.blocks, self.creatures]
        for i in range(len(file)):
            defined_assets = {}
            with open(file[i]) as block_file:
                for line in block_file:
                    # i.e Rock-A_int_radius.10,N_float_pos.5
                    raw_data = line.split('-')
                    # i.e A_int_radius.10,N_float_pos.5
                    attribute_info = raw_data[1].split(',')
                    # i.e A_int_radius.10
                    asset_name = raw_data[0]
                    attributes = {}
                    defined_assets[asset_name] = {}
                    for raw_attribute in attribute_info:
                        ri = raw_attribute.split('.')
                        # i.e [A_int_radius, 10]
                        raw_type = ri[0]
                        types = raw_type.split('_')
                        # i.e [[A, int, radius], 10]
                        value = ri[1]
                        if types[1] == 'int':
                            value = int(value)
                        elif types[1] == 'float':
                            value = float(value)
                        if types[0] == 'A':
                            attributes[types[2]] = value
                        else:
                            defined_assets[asset_name][types[2]] = value
                    defined_assets[asset_name]['attributes'] = attributes
            store[i] = defined_assets

    def _construct_content(self, content) -> None:
        sets = content.split('_')
        defined_blocks = {}

        # read in map data using loaded predefined blocks
        with open(sets[0]) as map_file:
            for row in map_file:
                row_blocks = []
                self.content['block'].append(row_blocks)

        with open(sets[1]) as creature_file:
            for creature in creature_file:
                row_blocks = []
                self.content['block'].append(row_blocks)


class Camera:
    """

    """
