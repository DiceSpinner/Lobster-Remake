from __future__ import annotations

from typing import Union, List, Optional, Dict, Any, Tuple
from data_structures import Queue
from error import IllegalConditionalOperatorError, NoneConditionError
from particles import Particle

OP_AND = 'and'
OP_OR = 'or'
OP_NOT = 'not'
OPERATORS = [OP_AND, OP_OR, OP_NOT]


class BoolExpr:
    """
    A boolean expression tree.

    === Private Attributes ===
    _root: The name of the attribute that will be applied by this BoolExpr.
    _condition: The required condition for _root to satisfy. The condition
        supports numerical boolean expressions that involves '<', '=', '>'.
    _subtrees: The list of all subtrees of this BoolExpr.

    === Representation Invariants ===
    - _operator Can either be any string or one of the operators defined above
    - len(_subtrees) == 0 when _operator is not an operator defined above
    - len(_subtrees) == 1 when _operator is OP_NOT
    - len(_subtrees) >= 2 when _operator is OP_AND or OP_OR
    - _condition is None if and only if _root is an operator
    - _condition can only contain one of '<', '=', '>'.
    - When _root == 'empty', this BoolExpr is empty and will always be
        evaluated True
    """
    _root: Optional[str]
    _subtrees: List[BoolExpr]
    _condition: Union[Tuple[str, Union[int, float]], bool, str]

    def __init__(self, root: str, subtrees: List[BoolExpr],
                 condition: Optional[Union[str, bool]]):
        """
        Initialize the BoolExpr with the given root and subtrees, an exception
        will be raised if the input condition is invalid.
        """
        self._root = root
        self._subtrees = subtrees[:]
        if root not in OPERATORS and not root == 'empty':
            if not isinstance(condition, bool):
                if condition is None:
                    raise NoneConditionError
                if condition[0] not in ['>', '=', '<']:
                    raise IllegalConditionalOperatorError
                condition = condition.split(' ')
                value = condition[1]
                if '.' in value:
                    value = float(value)
                else:
                    value = int(value)
                self._condition = (condition[0], value)
            else:
                self._condition = condition

    def __str__(self) -> str:
        """
        Returns the string representation of this BoolExpr

        >>> r1 = BoolExpr('health', [], '> 0')
        >>> print(r1)
        health > 0
        >>> r2 = BoolExpr('speed', [], '> 0')
        >>> print(r2)
        speed > 0
        >>> r3 = BoolExpr(OP_AND, [r1, r2], None)
        >>> print(r3)
        ( health > 0 and speed > 0 )
        >>> r4 = BoolExpr('collidable', [], True)
        >>> print(r4)
        collidable = True
        >>> r5 = BoolExpr('attack_damage', [], '= 0.5')
        >>> print(r5)
        attack_damage = 0.5
        >>> r6 = BoolExpr('vision', [], '= 6')
        >>> r7 = BoolExpr(OP_NOT, [r6], None)
        >>> print(r7)
        ( not vision = 6 )
        """
        if self._root == 'empty':
            return 'empty'
        if self._root not in OPERATORS:
            if isinstance(self._condition, bool):
                return self._root + ' = ' + str(self._condition)
            return self._root + ' ' + self._condition[0] + ' ' + \
                str(self._condition[1])
        s = ''
        if not self._root == OP_NOT:
            for i in range(len(self._subtrees)):
                s += self._subtrees[i].__str__()
                if i < (len(self._subtrees) - 1):
                    s += ' ' + self._root + ' '
            return '( ' + s + ' )'
        return '( not ' + self._subtrees[0].__str__() + ' )'

    def eval(self, particle: Particle) -> bool:
        """
        return the result of the application of this BoolExpr to the subject

        >>> r1 = BoolExpr('display_priority', [], '> 0')
        >>> ct = {'map_name':'none', 'x': 0, 'y': 0, 'vx': 0, 'vy': 0, 'ax': 0, \
            'ay': 0, 'display_priority': 0}
        >>> creep = Particle(ct)
        >>> r1.eval(creep)
        False
        >>> creep.display_priority = 1
        >>> r1.eval(creep)
        True
        >>> r2 = BoolExpr('display_priority', [], '< 0')
        >>> r2.eval(creep)
        False
        >>> creep.__setattr__('speed', 10)
        >>> r3 = BoolExpr('speed', [], '> 9')
        >>> r3.eval(creep)
        True
        >>> r4 = BoolExpr('and', [r1, r3], None)
        >>> r4.eval(creep)
        True
        >>> creep.speed = 0
        >>> r3.eval(creep)
        False
        """
        if self._root == 'empty':
            return True
        if self._root not in OPERATORS:
            if hasattr(particle, self._root):
                if self._condition == 'exist':
                    return True
                elif isinstance(self._condition, bool):
                    if not self._condition:
                        return not getattr(particle, self._root)
                    return getattr(particle, self._root)
                elif self._condition[0] == '<':
                    return getattr(particle, self._root) < self._condition[1]
                elif self._condition[0] == '>':
                    return getattr(particle, self._root) > self._condition[1]
                elif self._condition[0] == '=':
                    return getattr(particle, self._root) == self._condition[1]
            return False
        if self._root == OP_NOT:
            return not self._subtrees[0].eval(particle)
        if self._root == OP_OR:
            for subtree in self._subtrees:
                if subtree.eval(particle):
                    return True
            return False
        if self._root == OP_AND:
            for subtree in self._subtrees:
                if not subtree.eval(particle):
                    return False
            return True

    def append(self, subtree: BoolExpr) -> None:
        """
        Append the subtree to _subtrees
        """
        self._subtrees.append(subtree)


def construct_from_list(
        values: List[List[Union[str, Tuple[str, Union[str, bool]]]]]) -> BoolExpr:
    """
    Construct a BoolExpr from <values>.

    Precondition:
    <values> encodes a valid BoolExpr

    >>> lst = [[OP_OR], [('health', '> 0'), ('speed', '> 0')]]
    >>> r1 = construct_from_list(lst)
    >>> print(r1)
    ( health > 0 or speed > 0 )
    >>> lst2 = [[OP_NOT], [OP_AND], [('health', '> 0'), ('speed', '> 0')]]
    >>> r2 = construct_from_list(lst2)
    >>> print(r2)
    ( not ( health > 0 and speed > 0 ) )
    >>> lst3 = [[OP_OR], [OP_AND, ('a', '= 10')], [('b', '> 0'), ('c', '> 0')]]
    >>> r3 = construct_from_list(lst3)
    >>> print(r3)
    ( ( b > 0 and c > 0 ) or a = 10 )
    >>> lst4 = [[('health', '> 0')]]
    >>> r4 = construct_from_list(lst4)
    >>> print(r4)
    health > 0
    """
    begin = values[0][0]
    if begin not in OPERATORS:
        return BoolExpr(begin[0], [], begin[1])
    q = Queue()
    exp = BoolExpr(begin, [], None)
    for subtree in values[1]:
        q.enqueue((subtree, exp))
    index = 2
    while not q.is_empty():
        p = q.dequeue()
        if p[0] in OPERATORS:
            sub = BoolExpr(p[0], [], None)
            for subtree in values[index]:
                q.enqueue((subtree, sub))
            index += 1
        else:
            sub = BoolExpr(p[0][0], [], p[0][1])
        p[1].append(sub)

    return exp
