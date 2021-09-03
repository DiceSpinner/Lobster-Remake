from typing import Union, List, Tuple, Any, Callable
from error import UnknownTypeError
from expression_trees import ObjectAttributeEvaluator
import math
import settings
import importlib


class IfstreamObjectConstructor:
    """ Used to construct objects from txt files

    Input Format: <module.Class Name>
                  <Attribute1_datatype_value>
                  <Attribute2_datatype_value>
                  ......
    """
    _class_name: str
    _info: dict[str, Any]

    def __init__(self, path: str) -> None:
        """ Construct the dictionary representation of the particle with the
        input string

        Pre-condition: The input string is valid
        """
        self._info = {}
        with open(path, "r") as file:
            content = file.readlines()
            # separate class name and its fields
            class_name = content[0].rstrip()
            fields = content[1:]

            self._class_name = class_name

            # unpack the fields
            for field in fields:
                field = field.rstrip().split('~')
                attr = field[0]
                data_type = field[1]
                value = field[2]
                if data_type == 'int':
                    self._info[attr] = int(value)
                elif data_type == 'float':
                    self._info[attr] = float(value)
                elif data_type == 'bool':
                    if value == 'True':
                        self._info[attr] = True
                    else:
                        self._info[attr] = False
                elif data_type == 'str':
                    self._info[attr] = value
                elif data_type == 'eval':
                    self._info[attr] = eval(value)
                elif data_type == 'tuple':
                    value = value[1:len(value) - 1]
                    self._info[attr] = tuple(map(int, value.split(',')))
                elif data_type == 'ObjectAttributeEvaluator':
                    self._info[attr] = ObjectAttributeEvaluator(value)
                elif data_type == 'const':
                    self._info[attr] = evaluate(value)
                elif data_type == 'const_int':
                    self._info[attr] = int(evaluate(value))
                elif data_type == 'const_floor':
                    self._info[attr] = math.floor(evaluate(value))
                elif data_type == 'const_ceil':
                    self._info[attr] = math.ceil(evaluate(value))
                elif data_type == 'List_str':
                    self._info[attr] = to_list(value, str)
                else:
                    raise UnknownTypeError

    def get_attribute(self, key: str):
        return self._info[key]

    def has_attribute(self, key: str):
        return key in self._info

    def construct(self, extension: dict[str, Any], modules: List[str]) -> Any:
        """ Construct the object """
        class_name = None
        assert len(modules) > 0
        for module in modules:
            module = importlib.import_module(module)
            if hasattr(module, self._class_name):
                class_name = getattr(module, self._class_name)
                break
        assert class_name is not None
        tmp = self._info.copy()
        tmp.update(extension)
        return class_name(tmp)


def to_list(value: str, data_type: Callable) -> List[Any]:
    """ Convert 'value' to list of specified objects

    >>> s = '[1, 2, 3, 4]'
    >>> to_list(s, int)
    [1, 2, 3, 4]
    >>> to_list(s, str)
    ['1', '2', '3', '4']
    """
    value = value[1:-1].split(', ')  # remove brackets
    lst = []
    for item in value:
        lst.append(data_type(item))
    return lst


def evaluate(item: str) -> Any:
    """ Evaluate the input string and return the corresponding value from the
    settings.
    """
    item = item.split(" ")
    if len(item) == 1:
        return getattr(settings, item[0])
    elif len(item) == 3:
        if item[1] == "*":
            return getattr(settings, item[0]) * float(item[2])
        if item[1] == '/':
            return getattr(settings, item[0]) / float(item[2])
        if item[1] == '//':
            return int(getattr(settings, item[0]) // float(item[2]))
        if item[1] == '+':
            return getattr(settings, item[0]) + float(item[2])
        if item[1] == '-':
            return getattr(settings, item[0]) - float(item[2])
