from typing import Union
from error import UnknownTypeError


class PredefinedParticle:
    """ An object contains a dictionary representation of a predefined particle.

    Input Format: <Particle Name> <Class Name> <Attribute1_datatype_value>
        <Attribute2_datatype_value>...

    Required Fields:
        - Particle: display_priority, texture
        - Creature/Block: diameter, brightness, light_power, health, shape
    """
    info: dict[str, Union[str, int, float, bool]]

    def __init__(self, content: str) -> None:
        """ Construct the dictionary representation of the particle with the
        input string

        Pre-condition: The input string is valid
        """
        self.info = {}
        # split the string into segments
        content = content.split(' ')

        # separate class name and its fields
        particle_name = content[0]
        class_name = content[1]
        fields = content[2:]

        self.info['particle_name'] = particle_name
        self.info['class'] = class_name

        # unpack the fields
        for field in fields:
            field = field.split('_')
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
            else:
                raise UnknownTypeError


