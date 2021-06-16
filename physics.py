import pygame
from typing import List, Any, Tuple, Union
from game_objects import Particle
from rule import Rule, construct_from_list


class PhysicsApplicator:

    """
    Description: Applicators that apply physics rules

    === Public Attributes ===
    rules: Entities subject to this physics rule
    """
    subjects: List[Rule]

    def apply_physics(self, optional: List[Particle]) -> Any:
        raise NotImplementedError

    def applicable(self, particle: Particle) -> bool:
        """
        Return whether this rule can be applied to the particle
        """
        for rule in self.subjects:
            pass


class ForceApplicator(PhysicsApplicator):
    """
    Description: Collision rule applicator
    """
    def apply_physics(self, optional: List[Particle]) -> Any:
        pass


class CollisionApplicator(PhysicsApplicator):
    """
    Description: Collision rule applicator

    """

    def __init__(self):
        r = []
        self._rules = []
        
    def apply_physics(self, optional: List[Any]) -> Any:
        pass

