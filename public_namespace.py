""" This module can be accessed from everywhere else. """

import pygame
from error import UnknownTextureError
from typing import Tuple
from input_processor import InputProcessor

# input handling
input_handler = InputProcessor()

# loaded assets
images = {}
sounds = {}

# parameterized assets
par_images = {}

# Camera Scaling
Scale = 1

# Game map
game_map = {}  # dict[str, List[List[List[int]]]]
tile_map = {}


def get_texture_by_info(name: str, size: Tuple[int, int], direction: float,
                        alpha: int) \
        -> pygame.Surface:
    """ Return the texture with the given info, if texture with the given
    configuration does not exist generate the texture with this configuration
    and return it.
    """
    try:
        tup = (name, size, direction, alpha)
        try:
            return par_images[tup].copy()
        except KeyError:
            raw_texture = images[name]
            par_images[(name, raw_texture.get_size(), 0, 0)] = raw_texture
            scaled = pygame.transform.scale(raw_texture, size)
            rotated = pygame.transform.rotate(scaled, direction)
            rotated.set_alpha(alpha)
            par_images[tup] = rotated
            return rotated.copy()
    except KeyError:
        raise UnknownTextureError
