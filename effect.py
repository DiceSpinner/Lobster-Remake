import pygame
from typing import List, Any, Tuple, Union
from particles import Particle
from bool_expr import BoolExpr, construct_from_list


class Effect:

    """
    Effect that changes particle states

    === Public Attributes ===
    rules: A Rule object which indicates the subject of this effect
    """
    subjects: BoolExpr

    def apply_effect(self, particle: Particle, ) -> Any:
        """
        Apply this physical rule to objects
        """
        raise NotImplementedError

    def applicable(self, particle: Particle) -> bool:
        """
        Return whether this effect can be applied to the particle.
        """
        return self.subjects.eval(particle.attributes)


class Force(Effect):
    """
    Force effect applicator
    """
    def apply_effect(self, particle: Particle) -> Any:
        pass


class MultipleTargetsEffect(Effect):
    """
    Effect that affects multiple particles.
    """
    def apply_effect(self, particles: List[Particle]) -> Any:
        raise NotImplementedError


class CollisionEffect(MultipleTargetsEffect):

    def apply_effect(self, particle) -> Any:
        pass


class EffectOverTime(Effect):
    """
    Effect that affects particles over time
    """
    pass
