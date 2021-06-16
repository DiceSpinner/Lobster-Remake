from __future__ import annotations

from typing import Union, List, Optional, Dict, Any, Tuple
from data_structures import Queue
from error import IllegalConditionalOperatorError

OP_AND = 'and'
OP_OR = 'or'
OP_NOT = 'not'
OPERATORS = [OP_AND, OP_OR, OP_NOT]


class Rule:
    """
    Description: A boolean expression tree representing a rule.

    === Private Attributes ===
    _root: The name of the attribute that will be applied by this rule.
    _condition: The required condition for _root to satisfy. The condition
        supports boolean expressions that involves '<', '=', '>'.
    _subtrees: The list of all subtrees of this rule.

    === Representation Invariants ===
    - _operator Can either be any string or one of the operators defined above,
        len(_subtrees) == 0 in the former case and > 0 in the latter case.
    - _condition must be None when _root is an operator
    - _condition can only contain one of '<', '=', '>'.
    """
    _root: Optional[str]
    _subtrees: List[Rule]
    _condition: Union[Tuple[str, str], str]

    def __init__(self, root: str, subtrees: List[Rule],
                 condition: Optional[str]):
        """
        Initialize the rule with the given root and subtrees, an exception
        will be raised if the input condition is invalid.
        """
        self._root = root
        self._subtrees = subtrees[:]
        if root not in OPERATORS:
            if not (condition == 'true' or condition == 'false'):
                flag = False
                condition = condition.split(" ")
                operator = condition[0]
                content = condition[1]
                ops = ['<', '=', '>']

                for op in ops:
                    if op == operator:
                        flag = True
                if not flag or not content.isnumeric():
                    raise IllegalConditionalOperatorError
                self._condition = (condition[0], condition[1])
            else:
                self._condition = condition

    def __str__(self) -> str:
        """
        Returns the string representation of this rule

        >>> r1 = Rule('health', [], '> 0')
        >>> print(r1)
        health > 0
        >>> r2 = Rule('speed', [], '> 0')
        >>> print(r2)
        speed > 0
        >>> r3 = Rule('and', [r1, r2], None)
        >>> print(r3)
        ( health > 0 and speed > 0 )
        """
        if self._root not in OPERATORS:
            if self._condition == 'true' or self._condition == 'false':
                return self._root + ' == ' + self._condition
            return self._root + ' ' + self._condition[0] + ' ' + \
                self._condition[1]
        s = ''
        for i in range(len(self._subtrees)):
            s += self._subtrees[i].__str__()
            if i < (len(self._subtrees) - 1):
                s += ' ' + self._root + ' '
        return '( ' + s + ' )'

    def eval(self, content: Dict[str, Any]) -> bool:
        """
        return the result of the application of this rule to the content

        """
        if self._root not in OPERATORS:
            if self._root in content:
                if self._condition == 'true':
                    return content[self._root]
                if self._condition == 'false':
                    return not content[self._root]
                if '<' in self._condition:
                    return content[self._root] < str(self._condition[1])
                if '>' in self._condition:
                    return content[self._root] > str(self._condition[1])
                if '=' in self._condition:
                    return content[self._root] == str(self._condition[1])
            return False
        if self._root == OP_NOT:
            return not self._subtrees[0].eval(content)
        if self._root == OP_OR:
            for subtree in self._subtrees:
                if subtree.eval(content):
                    return True
            return False
        if self._root == OP_AND:
            for subtree in self._subtrees:
                if not subtree.eval(content):
                    return False
            return True


def construct_from_list(values: List[List[Union[str, int]]]) -> Rule:
    """
    Construct a rule from <values>.

    Precondition:
    <values> encodes a valid rule

    True


    root = values[0][0]
    if root not in OPERATORS:
        return Rule()
    q = Queue()
    for subtree in values[1]:
        q.enqueue((subtree, tree))
    index = 2
    while not q.is_empty():
        p = q.dequeue()
        sub = Rule(p[0], [])
        p[1].append(sub)
        if p[0] in OPERATORS:
            for subtree in values[index]:
                q.enqueue((subtree, sub))
            index += 1
    return tree
    """
    pass

