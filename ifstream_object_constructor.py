from typing import List, Any, Callable, TextIO, Tuple, Optional
from expression_trees import ObjectAttributeEvaluator
from error import CollidedObjectKeyError
import math
import settings
import importlib
import public_namespace


class _Constructor:
    """  """
    class_name: str
    info: dict[str, Any]
    key: Optional[str]

    def __init__(self, file_time: Tuple[TextIO, int], name: str) -> None:
        self.class_name = name
        self.info = {}
        self.key = None
        file, num = file_time
        while not num == 0:
            num -= 1
            try:
                field = next(file).strip().split('~')
                if len(field) == 2:
                    assert field[0] == 'key'
                    self.key = field[1]
                    continue
                attr, data_type, value = field
                if data_type == 'int':
                    self.info[attr] = int(value)
                elif data_type == 'float':
                    self.info[attr] = float(value)
                elif data_type == 'bool':
                    if value == 'True':
                        self.info[attr] = True
                    else:
                        self.info[attr] = False
                elif data_type == 'str':
                    self.info[attr] = value
                elif data_type == 'tuple':
                    value = value[1:len(value) - 1]
                    self.info[attr] = tuple(map(int, value.split(',')))
                elif data_type == 'ObjectAttributeEvaluator':
                    self.info[attr] = ObjectAttributeEvaluator(value)
                elif data_type == 'const':
                    self.info[attr] = evaluate(value)
                elif data_type == 'const_int':
                    self.info[attr] = int(evaluate(value))
                elif data_type == 'const_floor':
                    self.info[attr] = math.floor(evaluate(value))
                elif data_type == 'const_ceil':
                    self.info[attr] = math.ceil(evaluate(value))
                elif data_type == 'List_str':
                    self.info[attr] = to_list(value, str)
                elif data_type == 'predefined':
                    self.info[attr] = public_namespace.predefined_objects[value]
                elif data_type == 'extension':
                    n = int(value)
                    name = next(file).strip()
                    self.info[attr] = _Constructor((file, n), name)
            except StopIteration:
                break

    def construct(self, extension: dict[str, Any]) -> Any:
        """ Construct the object """
        module, name = self.class_name.split('.')
        module = importlib.import_module(module)
        if hasattr(module, name):
            name = getattr(module, name)
        tmp = self.info.copy()
        tmp.update(extension)
        for item in tmp:
            attr = tmp[item]
            if isinstance(attr, _Constructor) or \
                    isinstance(attr, IfstreamObjectConstructor):
                tmp[item] = attr.construct({})
        return name(tmp)


class IfstreamObjectConstructor:
    """ Used to construct objects from txt files

    Input Format: <module.Class Name>
                  <Attribute1_datatype_value>
                  <Attribute2_datatype_value>
                  ......

    Important Note: All classes being constructed must only accept a dictionary
        of variables for their constructors.
    """
    _constructor: _Constructor

    def __init__(self, path: str) -> None:
        """ Construct the dictionary representation of the particle with the
        input string

        Pre-condition: The input string is valid
        """
        with open(path, "r") as file:
            # separate class name and its fields
            class_name = next(file).rstrip()
            self._constructor = _Constructor((file, -1), class_name)
        key = self._constructor.key
        if key is not None:
            if key in public_namespace.predefined_objects:
                raise CollidedObjectKeyError
            public_namespace.predefined_objects[key] = self

    def get_attribute(self, key: str):
        return self._constructor.info[key]

    def has_attribute(self, key: str):
        return key in self._constructor.info

    def construct(self, extension: dict[str, Any]):
        return self._constructor.construct(extension)


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
