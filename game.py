import pygame
from physics import CollisionDetector
from typing import Tuple, Union, List


class Level:
    """
    Description:

    === Public Attributes ===
    setting
    """


class Game:
    """
    Description:

    === Private Attributes ===
        _asset_location: The locations of game assets
        _screen: Screen of the game that gets displayed to the player
        _screen_size: size of the screen
        _name: Name of the game
        _asset: Loaded assets of the game
        _levels: Levels of this game
    """
    _asset_location: List[str]
    _screen: pygame.Surface
    _screen_size: Tuple[int, int]
    _asset: dict[str, dict[str, Union[pygame.Surface, pygame.mixer.Sound, str]]]
    _levels: List[Level]

    def __init__(self, name: str, asset: [str],
                 screen_size: Tuple[int, int]) -> None:
        self._asset_location = asset
        self._name = name
        self._screen_size = screen_size

    def start(self):
        pygame.init()
        pygame.display.set_icon(pygame.image.load("Lobster_clean.png"))
        self._screen = pygame.display.set_mode(self._screen_size)
        pygame.display.set_caption(self._name)

        self._load_assets()

    def _load_assets(self) -> None:
        pygame.mixer.init()
        sound_format = ['wav']
        image_format = ['png', 'jpg', 'gif', 'bmp', 'tif']
        music_format = ['mp3', 'mp4']
        for location in self._asset_location:
            data = location.split('.')
            suffix = data[1]
            if suffix in sound_format:
                self._asset['sound'][data[0]] = pygame.mixer.Sound(location)
            elif suffix in image_format:
                self._asset['image'][data[0]] = pygame.image.load(location)
            elif suffix in music_format:
                self._asset['music'][data[0]] = data[1]


