from typing import Union, List, Tuple, Any, Callable
from error import UnknownTypeError
from expression_trees import ObjectAttributeEvaluator
import math
import settings


class PredefinedParticle:
    """ An object contains a dictionary representation of a predefined particle.

    Input Format: <Particle Name>
                  <Class Name>
                  <Attribute1_datatype_value>
                  <Attribute2_datatype_value>
                  ......

    Required Fields:
        - Particle: display_priority, texture
        - Creature/Block: diameter, brightness, light_power, health, shape
    """
    info: dict[str, Any]

    def __init__(self, path: str) -> None:
        """ Construct the dictionary representation of the particle with the
        input string

        Pre-condition: The input string is valid
        """
        self.info = {}
        with open(path, "r") as file:
            content = file.readlines()
            # separate class name and its fields
            particle_name = content[0].rstrip()
            class_name = content[1].rstrip()
            fields = content[2:]

            self.info['map_display'] = particle_name
            self.info['class'] = class_name

            # unpack the fields
            for field in fields:
                field = field.rstrip().split('~')
                attr = field[0]
                data_type = field[1]
                value = field[2]
                if data_type == 'int':
                    self.info[attr] = int(value)
                elif data_type == 'float':
                    self.info[attr] = float(value)
                elif data_type == 'bool':
                    self.info[attr] = bool(value)
                elif data_type == 'str':
                    self.info[attr] = value
                elif data_type == 'eval':
                    self.info[attr] = eval(value)
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
                else:
                    raise UnknownTypeError


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
