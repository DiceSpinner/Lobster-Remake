import pygame
from physics import *
from typing import Tuple, Union, List
import os


class Level:
    """
    Description: Levels of the game

    === Public Attributes ===
    difficulty: difficulty of the level

    === Private Attributes ===
    _asset: Loaded assets of the game
    _asset_location: The locations of game assets
    _physics: Sets of physics rules supported by this level

    === Representation Invariants ===
    - difficulty must be an integer from 0 - 3
    """
    difficulty: int
    _asset: dict[str, dict[str, Union[pygame.Surface, pygame.mixer.Sound, str]]]
    _asset_location: List[str]

    def __init__(self, asset: [str]):
        self._asset_location = asset

    def _load_assets(self) -> None:
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

    def run(self, screen: pygame.Surface, difficulty: int):
        """
        Run the level with the given setting
        """
        running = True
        while running:
            a = 1


class Game:
    """
    Description:
        A reusable game class

    === Private Attributes ===
        _screen: Screen of the game that gets displayed to the player
        _levels: Levels of this game
        _file: Path to the game files
        _base_dir: Base directory of the game
    """
    _base_dir: str
    _screen: pygame.Surface
    _levels: List[Level]
    _file: str

    def __init__(self, file: str) -> None:
        self._file = file

    def start(self) -> None:
        """
        Initialize the engine and start the game.
        """
        os.chdir(self._file)
        pygame.init()
        pygame.mixer.init()
        with open('asset_location.txt', 'r+') as game_file:
            setting = {}
            for line in game_file:
                line = line.split(':')
                setting[line[0]] = line[1]
            os.chdir(setting['name'])
            self._base_dir = os.getcwd()
            self._apply_settings(setting)
            self._load_level(setting['levels'])

    def _apply_settings(self, setting: dict[str, str]) -> None:
        """
        Apply game gui settings
        """
        pygame.display.set_icon(pygame.image.load(setting['icon']))
        size = setting['screen_size'].split(',')
        size = (int(size[0]), int(size[1]))
        self._screen = pygame.display.set_mode(size)
        pygame.display.set_caption(setting['name'])

    def _load_level(self, path: str) -> None:
        """
        Load levels from the "Levels" folder into the game.
        """
        os.chdir(path)
        levels = os.listdir()
        for lev in levels:
            with open(lev, 'r+') as level_file:
                self._levels.append(self._read_level(lev))

    def _read_level(self, lev) -> Level:
        pass

    def display_menu(self):
        return
