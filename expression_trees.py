from __future__ import annotations
from typing import Union, List, Optional, Any, Set
from data_structures import Queue
from error import UnknownAttributeError

FLOAT_ROUNDING = 2  # float numbers will be rounded to 2 digits
COMPOSITION_BEGIN = "("
COMPOSITION_END = ")"

OP_AND = 'and'
OP_OR = 'or'
OP_NOT = 'not'
LOGICAL_OPERATORS = [OP_AND, OP_OR, OP_NOT]

OP_ADD = '+'
OP_MINUS = '-'
OP_MULTIPLY = '*'
OP_DIVISION = '/'
OP_INT_DIVISION = '//'
NUM_OPERATORS = [OP_ADD, OP_MINUS, OP_MULTIPLY, OP_DIVISION, OP_INT_DIVISION]

OP_GREATER = ">"
OP_GT_EQ = ">="
OP_LESS = '<'
OP_LS_EQ = "<="
OP_EQUAL = '='
COMP_OPERATORS = [OP_GREATER, OP_LESS, OP_EQUAL, OP_GT_EQ, OP_LS_EQ]


class EmptyClass:
    """ Class used for testing purposes """
    pass


class ExprTree:
    """ Expression Tree Interface """
    _root: Union[str, int, float, bool]
    _subtrees: Optional[List[ExprTree]]

    def get_variables(self) -> Set[str]:
        """ Return a set of variables of this expression tree """
        returning = set()
        if not isinstance(self._root, str):
            return returning
        if self._root in LOGICAL_OPERATORS or self._root in NUM_OPERATORS or \
                self._root in COMP_OPERATORS:
            for tree in self._subtrees:
                returning = returning | tree.get_variables()
            return returning
        returning.add(self._root)
        return returning


class ValueExpr(ExprTree):
    """ A numeric expression tree """
    _root: Union[str, int, float]
    _subtrees: Optional[List[ValueExpr]]

    def __init__(self, root: Union[str, int, float],
                 subtrees: List[ValueExpr]) -> None:
        self._root = root
        self._subtrees = subtrees[:]

    def __str__(self) -> str:
        """ Returns a string representation of this expression tree

        >>> v1 = ValueExpr(1, [])
        >>> str(v1)
        '1'
        >>> v2 = ValueExpr(3, [])
        >>> str(v2)
        '3'
        >>> v3 = ValueExpr('+', [v1, v2])
        >>> str(v3)
        '( 1 + 3 )'
        >>> v4 = ValueExpr('x', [])
        >>> str(v4)
        'x'
        >>> v5 = ValueExpr('-', [v4, v3])
        >>> str(v5)
        '( x - ( 1 + 3 ) )'
        """
        if self._root in NUM_OPERATORS:
            return COMPOSITION_BEGIN + " " + str(self._subtrees[0]) + " " + \
                   self._root + " " + str(self._subtrees[1]) + " " + \
                   COMPOSITION_END
        return str(self._root)

    def eval(self, look_up: dict[str, Union[int, float]]) -> Union[int, float]:
        """ Evaluate this expression tree and returns the result

        >>> v1 = ValueExpr(1, [])
        >>> v1.eval({})
        1
        >>> v2 = ValueExpr(3, [])
        >>> v3 = ValueExpr("+", [v1, v2])
        >>> v3.eval({})
        4
        >>> v4 = ValueExpr('x', [])
        >>> v5 = ValueExpr("-", [v4, v3])
        >>> v5.eval({"x": 5})
        1
        """
        if self._root not in NUM_OPERATORS:
            if isinstance(self._root, str):
                return look_up[self._root]
            return self._root
        if self._root == OP_ADD:
            result = self._subtrees[0].eval(look_up) + \
                     self._subtrees[1].eval(look_up)
        elif self._root == OP_MINUS:
            result = self._subtrees[0].eval(look_up) - \
                     self._subtrees[1].eval(look_up)
        elif self._root == OP_MULTIPLY:
            result = self._subtrees[0].eval(look_up) * \
                     self._subtrees[1].eval(look_up)
        elif self._root == OP_DIVISION:
            result = self._subtrees[0].eval(look_up) / \
                     self._subtrees[1].eval(look_up)
        else:  # self._root == OP_INT_DIVISION
            result = self._subtrees[0].eval(look_up) // \
                     self._subtrees[1].eval(look_up)
        if isinstance(result, float):
            return round(result, FLOAT_ROUNDING)
        return result

    def substitute(self, look_up: dict[str, Union[int, float]]):
        """ Completely replace placeholder variables with actual numeric
        values
        """
        if self._root not in NUM_OPERATORS and isinstance(self._root, str):
            try:
                self._root = look_up[self._root]
            except KeyError:
                pass
            return
        for subtree in self._subtrees:
            subtree.substitute(look_up)

    def append(self, subtree: ValueExpr) -> None:
        """
        Append the subtree to _subtrees
        """
        assert isinstance(subtree, ValueExpr)
        self._subtrees.append(subtree)


class BoolExpr(ExprTree):
    """ A boolean expression tree evaluated on value expressions """
    _root: Union[bool, str]
    _subtrees: Optional[List[ValueExpr]]

    def __init__(self, root: Union[str, int, float],
                 subtrees: [List[ValueExpr]]) -> None:
        self._root = root
        self._subtrees = subtrees[:]

    def __str__(self) -> str:
        """ Returns a string representation of this expression tree

        >>> b1 = BoolExpr(True, [])
        >>> str(b1)
        'True'
        >>> v1 = ValueExpr(1, [])
        >>> v2 = ValueExpr(4, [])
        >>> b2 = BoolExpr(">", [v1, v2])
        >>> str(b2)
        '( 1 > 4 )'
        >>> v3 = ValueExpr("*", [v1, v2])
        >>> b3 = BoolExpr("=", [v1, v3])
        >>> str(b3)
        '( 1 = ( 1 * 4 ) )'
        >>> b4 = BoolExpr("x", [])
        >>> str(b4)
        'x'
        """
        if self._root in COMP_OPERATORS:
            return COMPOSITION_BEGIN + " " + str(self._subtrees[0]) + " " + \
                   str(self._root) + " " + str(self._subtrees[1]) + " " + \
                   COMPOSITION_END
        return str(self._root)

    def eval(self, look_up: dict[str, Union[int, float, bool]]) -> bool:
        """ Evaluate this boolean expression

        >>> b1 = BoolExpr(True, [])
        >>> b1.eval({})
        True
        >>> v1 = ValueExpr(1, [])
        >>> v2 = ValueExpr(4, [])
        >>> b2 = BoolExpr(">", [v1, v2])
        >>> b2.eval({})
        False
        >>> v3 = ValueExpr("*", [v1, v2])
        >>> b3 = BoolExpr("=", [v1, v3])
        >>> b3.eval({})
        False
        >>> v4 = ValueExpr("x", [])
        >>> v5 = ValueExpr("-", [v4, v3])
        >>> b4 = BoolExpr("<=", [v4, v5])
        >>> b4.eval({'x': 10})
        False

        """
        if self._root not in COMP_OPERATORS:
            if isinstance(self._root, str):
                return look_up[self._root]
            return self._root
        if self._root == OP_GREATER:
            return self._subtrees[0].eval(look_up) > self._subtrees[1].eval(
                look_up)
        if self._root == OP_LESS:
            return self._subtrees[0].eval(look_up) < self._subtrees[1].eval(
                look_up)
        if self._root == OP_GT_EQ:
            return self._subtrees[0].eval(look_up) >= self._subtrees[1].eval(
                look_up)
        if self._root == OP_LS_EQ:
            return self._subtrees[0].eval(look_up) <= self._subtrees[1].eval(
                look_up)
        if self._root == OP_EQUAL:
            return self._subtrees[0].eval(look_up) == self._subtrees[1].eval(
                look_up)

    def substitute(self, look_up: dict[str, Union[int, float, bool]]):
        """ Completely replace placeholder variables (includes ones in subtrees)
        with numeric/boolean values
        """
        if self._root not in COMP_OPERATORS and isinstance(self._root, str):
            try:
                self._root = look_up[self._root]
            except KeyError:
                pass
            return
        for subtree in self._subtrees:
            subtree.substitute(look_up)

    def append(self, subtree: ValueExpr) -> None:
        """
        Append the subtree to _subtrees
        """
        assert isinstance(subtree, ValueExpr)
        self._subtrees.append(subtree)


class LogicalBoolExpr(ExprTree):
    """
    A boolean expression tree that supports logical operators in addition to
    numeric comparisons.

    === Private Attributes ===
    _root: The root of this boolean expression.
    _subtrees: The list of all subtrees of this BoolExpr.

    === Representation Invariants ===
    - Every subtree and its descendant must not have variable name conflict
    """
    _root: Union[str, bool]
    _subtrees: List[Union[LogicalBoolExpr, BoolExpr]]

    def __init__(self, root: Union[str, bool],
                 subtrees: List[Union[LogicalBoolExpr, BoolExpr]]):
        """
        Initialize the BoolExpr with the given root and subtrees, an exception
        will be raised if the input condition is invalid.
        """
        self._root = root
        self._subtrees = subtrees[:]

    def __str__(self) -> str:
        """
        Returns the string representation of this BoolExpr

        >>> v1 = ValueExpr(1, [])
        >>> v2 = ValueExpr(2, [])
        >>> b1 = BoolExpr(">", [v1, v2])
        >>> cb1 = LogicalBoolExpr("not", [b1])
        >>> str(cb1)
        '( not ( 1 > 2 ) )'
        >>> b2 = BoolExpr("=", [v1, v2])
        >>> cb2 = LogicalBoolExpr("and", [b1, b2])
        >>> str(cb2)
        '( ( 1 > 2 ) and ( 1 = 2 ) )'
        >>> b3 = LogicalBoolExpr("or", [cb1, cb2])
        >>> str(b3)
        '( ( not ( 1 > 2 ) ) or ( ( 1 > 2 ) and ( 1 = 2 ) ) )'
        """
        if self._root not in LOGICAL_OPERATORS:
            return str(self._root)
        if self._root == OP_NOT:
            return COMPOSITION_BEGIN + " " + OP_NOT + " " + \
                   str(self._subtrees[0]) + " " + COMPOSITION_END
        return COMPOSITION_BEGIN + " " + str(self._subtrees[0]) + " " + \
            self._root + " " + str(self._subtrees[1]) + " " + COMPOSITION_END

    def eval(self, look_up: dict[str, Union[int, float, bool]]) -> bool:
        """
        Evaluates this boolean expression and returns the result

        >>> v1 = ValueExpr(1, [])
        >>> v2 = ValueExpr(2, [])
        >>> b1 = BoolExpr(">", [v1, v2])
        >>> cb1 = LogicalBoolExpr("not", [b1])
        >>> cb1.eval({})
        True
        >>> b2 = BoolExpr("=", [v1, v2])
        >>> cb2 = LogicalBoolExpr("and", [b1, b2])
        >>> cb2.eval({})
        False
        >>> cb3 = LogicalBoolExpr("x", [])
        >>> cb3.eval({"x": True})
        True
        >>> cb4 = LogicalBoolExpr("or", [cb1, cb3])
        >>> cb4.eval({"y": True, "x": False})
        True
        """
        if isinstance(self._root, bool):
            return self._root
        if self._root not in LOGICAL_OPERATORS:
            return look_up[self._root]
        if self._root == OP_NOT:
            return not self._subtrees[0].eval(look_up)
        if self._root == OP_OR:
            for subtree in self._subtrees:
                if subtree.eval(look_up):
                    return True
            return False
        if self._root == OP_AND:
            for subtree in self._subtrees:
                if not subtree.eval(look_up):
                    return False
            return True

    def append(self, subtree: Union[LogicalBoolExpr, BoolExpr]) -> None:
        """
        Append the subtree to _subtrees
        """
        assert isinstance(subtree, BoolExpr) or \
               isinstance(subtree, LogicalBoolExpr)
        self._subtrees.append(subtree)


class ObjectAttributeEvaluator:
    """ A condition checker that uses boolean expressions to evaluate on
    object attributes.

    === Private Attributes ===
    - _condition: A boolean expression used for evaluation
    - _evaluating: A set of attributes that will be evaluated
    """
    _condition: Union[BoolExpr, LogicalBoolExpr]
    _evaluating: Set[str]

    def __init__(self, condition: Union[str, LogicalBoolExpr]) -> None:
        if isinstance(condition, str):
            if is_logical(condition):
                self._condition = construct_logical_bool_from_str(condition)
            else:
                self._condition = construct_bool_from_str(condition)
        else:
            assert isinstance(condition, LogicalBoolExpr) or \
                   isinstance(condition, BoolExpr)
            self._condition = condition
        self._evaluating = self._condition.get_variables()

    def eval(self, obj: Any) -> bool:
        """ Evaluate the attributes of this object

        >>> e1 = ObjectAttributeEvaluator('( x < 1 )')
        >>> o = EmptyClass()
        >>> setattr(o, 'x', 2)
        >>> e1.eval(o)
        False
        >>> s2 = '( ( health > 0 ) and ( speed > 0 ) )'
        >>> e2 = ObjectAttributeEvaluator(s2)
        >>> setattr(o, 'health', 10)
        >>> setattr(o, 'speed', 2)
        >>> e2.eval(o)
        True
        >>> setattr(o, 'health', 0)
        >>> e2.eval(o)
        False
        """
        look_up = {}
        for item in self._evaluating:
            look_up[item] = getattr(obj, item)
        return self._condition.eval(look_up)


class MultiObjectsEvaluator:
    """ A condition checker that uses boolean expressions to evaluate on
    attributes of multiple objects. All variables used in expression trees must
    have prefixes end with an underscore "_" to indicate which object it belongs
    to when evaluating.

    === Private Attribute ===
    - _condition: A boolean expression used for evaluation
    - _evaluating: A set of attributes that will be evaluated
    """
    _condition: Union[BoolExpr, LogicalBoolExpr]
    _evaluating: dict[str, Set[str]]

    def __init__(self, condition: Union[str, LogicalBoolExpr]) -> None:
        if isinstance(condition, str):
            if is_logical(condition):
                self._condition = construct_logical_bool_from_str(condition)
            else:
                self._condition = construct_bool_from_str(condition)
        else:
            assert isinstance(condition, LogicalBoolExpr) or isinstance(
                condition, BoolExpr)
            self._condition = condition
        vs = self._condition.get_variables()
        self._evaluating = {}
        for v in vs:
            index = v.find("_")
            if index == -1 or index == 0:
                raise UnknownAttributeError
            prefix = v[0:index]
            variable = v[index + 1:]
            if prefix not in self._evaluating:
                self._evaluating[prefix] = set()
            self._evaluating[prefix].add(variable)

    def eval(self, objs: dict[str, Any]) -> bool:
        """ Evaluate attributes of passed in objects

        >>> o1 = EmptyClass()
        >>> o2 = EmptyClass()
        >>> setattr(o1, 'x', 2)
        >>> setattr(o2, 'x', 4)
        >>> contract = {'self': o1, 'other': o2}
        >>> o1.x = 5
        >>> s2 = '( ( self_x > 0 ) and ( other_y >= -1 ) )'
        >>> e2 = MultiObjectsEvaluator(s2)
        >>> setattr(o2, 'y', 1)
        >>> e2.eval(contract)
        True
        """
        look_up = {}
        for prefix in objs:
            obj = objs[prefix]
            attrs = self._evaluating[prefix]
            for attr in attrs:
                look_up[prefix + "_" + attr] = getattr(obj, attr)
        return self._condition.eval(look_up)

    def get_attrs(self) -> dict[str, Set[str]]:
        """ Return the set of attributes that will be evaluated for each
        object.
        """
        r = {}
        for key in self._evaluating:
            r[key] = self._evaluating[key].copy()
        return r


def construct_value_from_list(lst: List[List[Union[str, int, float]]]) -> \
        ValueExpr:
    """ Construct a value expression from list

    >>> lst1 = [['+'], [1, 2]]
    >>> v1 = construct_value_from_list(lst1)
    >>> str(v1)
    '( 1 + 2 )'
    """
    begin = lst[0][0]
    expr = ValueExpr(begin, [])
    if begin not in NUM_OPERATORS:
        return expr
    q = Queue()
    for subtree in lst[1]:
        q.enqueue((subtree, expr))
    index = 2
    while not q.is_empty():
        p = q.dequeue()
        sub = ValueExpr(p[0], [])
        if p[0] in NUM_OPERATORS:
            for subtree in lst[index]:
                q.enqueue((subtree, sub))
            index += 1
        p[1].append(sub)
    return expr


def divide_by_space_brackets(s: List[str]) -> List[str]:
    """ Separate the string by brackets and spaces

    >>> s1 = ["1", "2", "(", "2", ")", "4", "5"]
    >>> divide_by_space_brackets(s1)
    ['1', '2', '( 2 )', '4', '5']
    >>> s2 = ['1', '2', '3', '(', '(', '4', '5', ')', ')', '5']
    >>> divide_by_space_brackets(s2)
    ['1', '2', '3', '( ( 4 5 ) )', '5']
    >>> s3 = ['(', '1', ')']
    >>> divide_by_space_brackets(s3)
    ['( 1 )']
    """
    lst = []
    bracket = False
    bs = "( "
    count = 0
    for item in s:
        if not bracket:
            if not item == "(":
                lst.append(item)
            else:
                bracket = True
        else:
            bs += item + " "
            if item == "(":
                count += 1
            elif item == ")":
                count -= 1
            if count < 0:
                lst.append(bs.rstrip())
                bracket = False
                bs = "( "
                count = 0
    return lst


def construct_value_from_str(s: str) -> ValueExpr:
    """ Construct a value expression from the string representation

    >>> s1 = "( 1 + 2 )"
    >>> v1 = construct_value_from_str(s1)
    >>> str(v1)
    '( 1 + 2 )'
    >>> s2 = "( x + ( 2 - 5 ) )"
    >>> v2 = construct_value_from_str(s2)
    >>> str(v2)
    '( x + ( 2 - 5 ) )'
    >>> s3 = "( 1 + ( 2 - ( 3 * 4 ) ) )"
    >>> v3 = construct_value_from_str(s3)
    >>> str(v3)
    '( 1 + ( 2 - ( 3 * 4 ) ) )'
    >>> s4 = '-1'
    >>> v4 = construct_value_from_str(s4)
    >>> str(v4)
    '-1'

    """
    if s.lstrip('-').isnumeric():
        # isnumeric() fails on negative numbers,
        # must remove '-' before checking
        value = to_num(s)
        return ValueExpr(value, [])
    elif s not in NUM_OPERATORS and " " not in s:  # when "s" is a variable
        return ValueExpr(s, [])
    if s[0] == '(' and s[-1] == ')':
        s = s[1:-1]  # remove outer brackets and spaces
    s = divide_by_space_brackets(s.strip().split(" "))
    assert len(s) == 3
    assert s[1] in NUM_OPERATORS
    return ValueExpr(s[1], [construct_value_from_str(s[0]),
                            construct_value_from_str(s[2])])


def construct_bool_from_str(s: str) -> BoolExpr:
    """ Construct a boolean expression from the string

    >>> s1 = "( 1 < 2 )"
    >>> b1 = construct_bool_from_str(s1)
    >>> str(b1)
    '( 1 < 2 )'
    >>> s2 = "True"
    >>> b2 = construct_bool_from_str(s2)
    >>> str(b2)
    'True'
    >>> s3 = 'False'
    >>> b3 = construct_bool_from_str(s3)
    >>> str(b3)
    'False'
    >>> s4 = '( ( 1 + 2 ) = 10 )'
    >>> b4 = construct_bool_from_str(s4)
    >>> str(b4)
    '( ( 1 + 2 ) = 10 )'
    >>> s5 = "( ( 3 - 1 ) >= ( 4 * 8 ) )"
    >>> b5 = construct_bool_from_str(s5)
    >>> str(b5)
    '( ( 3 - 1 ) >= ( 4 * 8 ) )'
    >>> s6 = "( ( 3 - 1 ) <= ( 4 * ( 2 + 3 ) ) )"
    >>> b6 = construct_bool_from_str(s6)
    >>> str(b6)
    '( ( 3 - 1 ) <= ( 4 * ( 2 + 3 ) ) )'
    """
    if s == "True":
        return BoolExpr(True, [])
    elif s == 'False':
        return BoolExpr(False, [])
    s = s[1:-1]  # remove outer brackets and spaces
    s = divide_by_space_brackets(s.strip().split(" "))
    assert len(s) == 3
    assert s[1] in COMP_OPERATORS
    return BoolExpr(s[1], [construct_value_from_str(s[0]),
                           construct_value_from_str(s[2])])


def construct_logical_bool_from_str(s: str) -> LogicalBoolExpr:
    """ Construct a logical boolean expression from the string representation

    >>> s1 = '( ( 1 < 2 ) and True )'
    >>> l1 = construct_logical_bool_from_str(s1)
    >>> str(l1)
    '( ( 1 < 2 ) and True )'
    >>> s2 = '( ( 1 < 2 ) and ( True or False ) )'
    >>> l2 = construct_logical_bool_from_str(s2)
    >>> str(l2)
    '( ( 1 < 2 ) and ( True or False ) )'
    >>> s3 = '( not ( x = 2 ) )'
    >>> l3 = construct_logical_bool_from_str(s3)
    >>> str(l3)
    '( not ( x = 2 ) )'
    """
    if s == "True":
        return LogicalBoolExpr(True, [])
    elif s == 'False':
        return LogicalBoolExpr(False, [])
    s = s[1:-1]  # remove outer brackets and spaces
    s = divide_by_space_brackets(s.strip().split(" "))
    assert len(s) == 3 or len(s) == 2
    if len(s) == 3:
        assert s[1] in LOGICAL_OPERATORS
        if is_logical(s[0]):
            b1 = construct_logical_bool_from_str(s[0])
        else:
            b1 = construct_bool_from_str(s[0])
        if is_logical(s[2]):
            b2 = construct_logical_bool_from_str(s[2])
        else:
            b2 = construct_bool_from_str(s[2])
        return LogicalBoolExpr(s[1], [b1, b2])
    else:
        assert s[0] in LOGICAL_OPERATORS
        if is_logical(s[1]):
            b1 = construct_logical_bool_from_str(s[1])
        else:
            b1 = construct_bool_from_str(s[1])
        return LogicalBoolExpr(s[0], [b1])


def is_logical(s: str) -> bool:
    for operator in LOGICAL_OPERATORS:
        if operator in s:
            return True
    return False


def to_num(s: str) -> Union[int, float]:
    if "." in s:
        return float(s)
    return int(s)
