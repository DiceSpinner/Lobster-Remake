from __future__ import annotations

from typing import Union, List, Optional, Dict, Any, Tuple
from data_structures import Queue
from error import IllegalConditionalOperatorError, NoneConditionError, \
    MainConnectiveError

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
                 condition: Optional[Union[bool, Tuple[str, str]]]):
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

        >>> r1 = BoolExpr('health', [], ('>', '0'))
        >>> print(r1)
        health > 0
        >>> r2 = BoolExpr('speed', [], ('>', '0'))
        >>> print(r2)
        speed > 0
        >>> r3 = BoolExpr(OP_AND, [r1, r2], None)
        >>> print(r3)
        ( health > 0 and speed > 0 )
        >>> r4 = BoolExpr('collidable', [], True)
        >>> print(r4)
        collidable = True
        >>> r5 = BoolExpr('attack_damage', [], ('=', '0.5'))
        >>> print(r5)
        attack_damage = 0.5
        >>> r6 = BoolExpr('vision', [], ('=', '6'))
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

    def eval(self, info: dict[str, Union[str, int, float, bool]]) -> bool:
        """
        return the result of the application of this BoolExpr to the subject

        >>> r1 = BoolExpr('display_priority', [], ('>', '0'))
        >>> ct = {'map_name':'none', 'x': 0, 'y': 0, 'vx': 0, 'vy': 0, 'ax': 0, \
            'ay': 0, 'display_priority': 0}
        >>> r1.eval(ct)
        False
        >>> ct['display_priority'] = 1
        >>> r1.eval(ct)
        True
        >>> r2 = BoolExpr('display_priority', [], ('<', '0'))
        >>> r2.eval(ct)
        False
        >>> ct['speed'] = 10
        >>> r3 = BoolExpr('speed', [], ('>', '9'))
        >>> r3.eval(ct)
        True
        >>> r4 = BoolExpr('and', [r1, r3], None)
        >>> r4.eval(ct)
        True
        >>> ct['speed'] = 0
        >>> r3.eval(ct)
        False
        """
        if self._root == 'empty':
            return True
        if self._root not in OPERATORS:
            if self._root in info:
                if self._condition == 'exist':
                    return True
                elif isinstance(self._condition, bool):
                    if not self._condition:
                        return not info[self._root]
                    return info[self._root]
                elif self._condition[0] == '<':
                    return info[self._root] < self._condition[1]
                elif self._condition[0] == '>':
                    return info[self._root] > self._condition[1]
                elif self._condition[0] == '=':
                    return info[self._root] == self._condition[1]
            return False
        if self._root == OP_NOT:
            return not self._subtrees[0].eval(info)
        if self._root == OP_OR:
            for subtree in self._subtrees:
                if subtree.eval(info):
                    return True
            return False
        if self._root == OP_AND:
            for subtree in self._subtrees:
                if not subtree.eval(info):
                    return False
            return True

    def append(self, subtree: BoolExpr) -> None:
        """
        Append the subtree to _subtrees
        """
        self._subtrees.append(subtree)


def construct_from_list(
        values: List[List[Union[str,
                                Tuple[str, Union[str, bool],
                                      Optional[str]]]]]) -> BoolExpr:
    """
    Construct a BoolExpr from <values>.

    Precondition:
    <values> encodes a valid BoolExpr

    >>> lst = [[OP_OR], [('health','>', '0'), ('speed','>', '0')]]
    >>> r1 = construct_from_list(lst)
    >>> print(r1)
    ( health > 0 or speed > 0 )
    >>> lst2 = [[OP_NOT], [OP_AND], [('health', '>', '0'), ('speed', '>', '0')]]
    >>> r2 = construct_from_list(lst2)
    >>> print(r2)
    ( not ( health > 0 and speed > 0 ) )
    >>> lst3 = [[OP_OR], [OP_AND, ('a', '=', '10')], [('b', '>', '0'), ('c', '>', '0')]]
    >>> r3 = construct_from_list(lst3)
    >>> print(r3)
    ( ( b > 0 and c > 0 ) or a = 10 )
    >>> lst4 = [[('health', '>', '0')]]
    >>> r4 = construct_from_list(lst4)
    >>> print(r4)
    health > 0
    """
    begin = values[0][0]
    if begin not in OPERATORS:
        return BoolExpr(begin[0], [], (begin[1], begin[2]))
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
            sub = BoolExpr(p[0][0], [], (p[0][1], p[0][2]))
        p[1].append(sub)

    return exp


def construct_from_str(info: str) -> BoolExpr:
    """ Construct a BoolExpr with the input string.

    Pre-condition: info follows the string format of BoolExpr

    >>> s = "( health > 0 or speed > 0 )"
    >>> b1 = construct_from_str(s)
    >>> print(b1)
    ( health > 0 or speed > 0 )
    >>> s = "( not ( health > 0 and speed > 0 ) )"
    >>> b2 = construct_from_str(s)
    >>> print(b2)
    ( not ( health > 0 and speed > 0 ) )
    >>> s = "( ( b > 0 and c > 0 ) or a = 10 )"
    >>> b3 = construct_from_str(s)
    >>> print(b3)
    ( ( b > 0 and c > 0 ) or a = 10 )
    >>> s = "health > 0"
    >>> b4 = construct_from_str(s)
    >>> print(b4)
    health > 0
    >>> s = "( not vision = 6 )"
    >>> b5 = construct_from_str(s)
    >>> print(s)
    ( not vision = 6 )
    """
    lst = [[]]
    info = info.split(" ")
    queue = Queue()
    queue.enqueue((info, 0))
    i = 0
    while not queue.is_empty():
        raw = queue.dequeue()
        item = raw[0]
        index = raw[1]
        try:
            result = _main_connective_separate(item)
            lst[index].append(result['main_connective'])
            lst.append([])
            i += 1
            for item in result['expr']:
                queue.enqueue((item, i))
        except MainConnectiveError:
            if item[0] == "(" and item[-1] == ")":
                item = item[1:-1]
            attr = item[0]
            comparator = item[1]
            value = item[2]
            lst[index].append((attr, comparator, value))
    return construct_from_list(lst)


def _main_connective_separate(items: List[str]) -> \
        Dict[str, Union[List[List[str]], str]]:
    """ Separate the main connective from the rest of the bool expression

    >>> l = ['(', 'health', ">", '0', 'or', 'speed', '>', '0', ')']
    >>> r = _main_connective_separate(l)
    >>> print(r)
    {'main_connective': 'or', 'expr': [['health', '>', '0'], ['speed', '>', '0']]}
    """
    lst = {
        'main_connective': 0,
        'expr': []
    }
    if items[0] == "(" and items[-1] == ")":
        items = items[1:-1]
    else:
        raise MainConnectiveError
    count = 0
    for i in range(len(items)):
        item = items[i]
        if item == '(':
            count += 1
        elif item == ')':
            count -= 1
        elif count == 0 and item in OPERATORS:
            lst['main_connective'] = item
            if i == 0:
                lst['expr'].append(items[1:])
            else:
                lst['expr'].append(items[:i])
                lst['expr'].append(items[i + 1:])
    return lst
