from typing import Union, List, Tuple
from error import UnknownTypeError
from bool_expr import construct_from_str, BoolExpr


class PredefinedParticle:
    """ An object contains a dictionary representation of a predefined particle.

    Input Format: <Particle Name> <Class Name> <Attribute1_datatype_value>
        <Attribute2_datatype_value>...

    Required Fields:
        - Particle: display_priority, texture
        - Creature/Block: diameter, brightness, light_power, health, shape
    """
    info: dict[str, Union[str, int, float, bool, List, Tuple, BoolExpr]]

    def __init__(self, content: str) -> None:
        """ Construct the dictionary representation of the particle with the
        input string

        Pre-condition: The input string is valid
        """
        self.info = {}
        # split the string into segments
        content = content.split('  ')

        # separate class name and its fields
        particle_name = content[0].rstrip()
        class_name = content[1].rstrip()
        fields = content[2:]

        self.info['name'] = particle_name
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
            elif data_type == 'BoolExpr':
                self.info[attr] = construct_from_str(value)
            else:
                raise UnknownTypeError


