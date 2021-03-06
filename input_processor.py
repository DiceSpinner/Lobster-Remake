import pygame
from typing import Set, List, Tuple


class InputProcessor:
    """ Handler for user inputs

    === Private Attributes ===
    - _pressed_keys: A set of pressed_keys during the previous frame
    """
    _pressed_keys: dict[int, int]
    _key_up: dict[int, int]
    _mouse_button_clicked: dict[int, int]
    _mouse_button_up: dict[int, int]
    _mouse_pos: Tuple[int, int]
    running: bool

    def __init__(self) -> None:
        self._pressed_keys = {}
        self._key_up = {}
        self._events = []
        self._mouse_button_clicked = {}
        self._mouse_button_up = {}
        self._mouse_pos = (0, 0)
        self.running = True

    def process_input(self, events: List[pygame.event.Event],
                      mouse_pos: Tuple[int, int]):
        """ Process input from the user """
        self._key_up = {}
        self._mouse_button_up = {}
        self._mouse_pos = mouse_pos
        for event in events:
            if event.type == pygame.KEYDOWN:
                self._pressed_keys[event.key] = 0
            elif event.type == pygame.KEYUP:
                assert event.key in self._pressed_keys
                self._key_up[event.key] = self._pressed_keys[event.key]
                self._pressed_keys.pop(event.key, None)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self._mouse_button_clicked[event.button] = 0
            elif event.type == pygame.MOUSEBUTTONUP:
                assert event.button in self._mouse_button_clicked
                self._mouse_button_up[event.button] = \
                    self._mouse_button_clicked[event.button]
                self._mouse_button_clicked.pop(event.button, None)
            elif event.type == pygame.QUIT:
                self.running = False
        for key in self._pressed_keys:
            self._pressed_keys[key] += 1
        for button in self._mouse_button_clicked:
            self._mouse_button_clicked[button] += 1

    def get_key_up(self):
        return self._key_up.copy()

    def get_key_pressed(self):
        return self._pressed_keys.copy()

    def get_mouse_button_clicked(self):
        return self._mouse_button_clicked.copy()

    def get_mouse_button_up(self):
        return self._mouse_button_up.copy()

    def get_mouse_pos(self):
        return self._mouse_pos
