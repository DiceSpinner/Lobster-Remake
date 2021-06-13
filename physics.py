import pygame
from typing import List, Any, Tuple, Union


class PhysicsApplicator:

    """
    Description: Applicators that apply physics rules

    === Public Attributes ===
    subjects: Entities subject to this physics rule
    """
    subjects: str

    def apply_physics(self, optional: List[Any]) -> Any:
        raise NotImplementedError


class CollisionApplicator(PhysicsApplicator):
    """
    Description: Collision rule applicator

    === Public Attributes ===
    subjects: Entities subject to this physics rule
    """
    subjects: []

    def __init__(self):
        self.subjects = ['collidable']

    def apply_physics(self, optional: List[Any]) -> Any:
        raise NotImplementedError

