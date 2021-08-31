import pygame
from typing import Set, List, Tuple


class InputProcessor:
    """ Handler for user inputs

    === Private Attributes ===
    - _pressed_keys: A set of pressed_keys during the previous frame
    """
    _pressed_keys: dict[int, int]
    _current_pressed: Set[int]
    _key_up: Set[int]
    _mouse_pos: Tuple[bool]
    running: bool

    def __init__(self) -> None:
        self._pressed_keys = {}
        self._current_pressed = set()
        self._key_up = set()
        self._events = []
        self.running = True

    def process_input(self, events: List[pygame.event.Event]):
        """ Process input from the user """
        self._key_up = set()
        self._current_pressed = set()
        self._events = pygame.event.get()
        for event in events:
            if event.type == pygame.KEYDOWN:
                try:
                    self._pressed_keys[event.key] += 1
                except KeyError:
                    self._pressed_keys[event.key] = 1
                self._current_pressed.add(event.key)
            elif event.type == pygame.KEYUP:
                self._key_up.add(event.key)
                self._pressed_keys.pop(event.key, None)
            elif event.type == pygame.QUIT:
                self.running = False

    def get_key_up(self):
        return self._key_up.copy()

    def get_key_pressed(self):
        return self._pressed_keys.copy()

