from __future__ import annotations
import pygame
from typing import List, Tuple, Union, Optional, Any
from utilities import Positional, Movable, Collidable, Lightable, Living, \
    Directional, Attackable, get_direction, DynamicStats, called
from bool_expr import BoolExpr, construct_from_str
from settings import *
from error import InvalidConstructionInfo


class Particle(Positional, DynamicStats):
    """
    Description: Customized sprites

    === Public Attributes ===
    - id: Identifier of the particle.
    - display_priority: The display priority of this particle, particles with
        the highest priority will be displayed on top of the screen

    - name: Name of this particle (displayed in map txt file)

    === Private Attributes ===
    -
    """
    # static fields
    ID = 0
    particle_group = {}
    light_particles = {}
    textures = {}
    rotation = {}
    sounds = {}

    id: int
    display_priority: int
    texture: str
    _texture: pygame.Surface
    name: str
    detection_radius: int
    _surrounding_tiles: dict[int, dict[int, Particle]]
    _surrounding_entities: dict[int, dict[int, List[Particle]]]

    def __init__(self, info: dict[str, Union[str, float, int]]) -> None:
        if called(self.__class__.__name__, info):
            return
        default = {
            'display_priority': DEFAULT_DISPLAY_PRIORITY,
            'texture': DEFAULT_PARTICLE_TEXTURE,
            'name': DEFAULT_PARTICLE_NAME,
            'detection_radius': DEFAULT_DETECTION_RADIUS
        }
        attr = ['display_priority', 'texture', 'name', 'detection_radius']
        Positional.__init__(self, info)
        DynamicStats.__init__(self)
        self.id = Particle.ID
        Particle.ID += 1
        for key in default:
            if key not in info:
                info[key] = default[key]
        for item in info:
            if item in attr:
                setattr(self, item, info[item])
        self._texture = Particle.textures[self.texture]
        self._surrounding_tiles = []
        self._surrounding_entities = []
        Particle.particle_group[self.id] = self

    def display(self, screen: pygame.Surface,
                location: Tuple[int, int]) -> None:
        screen.blit(self._texture, location)

    def remove(self):
        """ Remove this particle from the game """
        Particle.particle_group.pop(self.id, None)

    def update_surroundings(self, tiles: dict[int, dict[int, Particle]],
                            entities: dict[int, dict[int, List[Particle]]]):
        self._surrounding_tiles = tiles
        self._surrounding_entities = entities

    def get_adjacent_entities(self, diagonal=False) -> List[Particle]:
        if isinstance(self, Collidable):
            center_x = int((self.x - 1 + self.diameter / 2) // TILE_SIZE)
            center_y = int((self.y - 1 + self.diameter / 2) // TILE_SIZE)
        else:
            center_x = int((self.x // TILE_SIZE))
            center_y = int((self.y // TILE_SIZE))

        left = (center_x - 1, center_y)
        top = (center_x, center_y - 1)
        right = (center_x + 1, center_y)
        down = (center_x, center_y + 1)
        returning = [left, top, right, down, (center_x, center_y)]
        if diagonal:
            top_left = (center_x - 1, center_y - 1)
            top_right = (center_x + 1, center_y - 1)
            bottom_right = (center_x + 1, center_y + 1)
            bottom_left = (center_x - 1, center_y + 1)
            returning += [top_right, top_left, bottom_right, bottom_left]
        lst = []
        for item in returning:
            if item[1] in self._surrounding_entities:
                if item[0] in self._surrounding_entities[item[1]]:
                    lst += self._surrounding_entities[item[1]][item[0]]
        return lst

    def get_adjacent_tiles(self, diagonal=False) -> List[Particle]:
        if isinstance(self, Collidable):
            center_x = int((self.x - 1 + self.diameter / 2) // TILE_SIZE)
            center_y = int((self.y - 1 + self.diameter / 2) // TILE_SIZE)
        else:
            center_x = int((self.x // TILE_SIZE))
            center_y = int((self.y // TILE_SIZE))

        left = (center_x - 1, center_y)
        top = (center_x, center_y - 1)
        right = (center_x + 1, center_y)
        down = (center_x, center_y + 1)
        returning = [left, top, right, down]
        if diagonal:
            top_left = (center_x - 1, center_y - 1)
            top_right = (center_x + 1, center_y - 1)
            bottom_right = (center_x + 1, center_y + 1)
            bottom_left = (center_x - 1, center_y + 1)
            returning += [top_right, top_left, bottom_right, bottom_left]
        lst = []
        for item in returning:
            if item[1] in self._surrounding_tiles:
                if item[0] in self._surrounding_tiles[item[1]]:
                    lst.append(self._surrounding_tiles[item[1]][item[0]])
        return lst

    def __str__(self):
        return self.name


class Item(Collidable, Particle):
    """ Description: An object represents an item in game

    """
    pass


class CollidableParticle(Particle, Collidable):
    def __init__(self, info: dict[str, Union[str, float, int, Tuple]]) -> None:
        if called(self.__class__.__name__, info):
            return
        Particle.__init__(self, info)
        Collidable.__init__(self, info)
        self._texture = pygame.transform.scale(self._texture,
                                               (self.diameter, self.diameter))


class CollisionBox(CollidableParticle):
    """ A stationary particle used to collision detection

    === Public Attributes ===
    _ self_destroy: Ticks before self-destruction
    - owner: The particle that created this collision box

    === Private Attributes ===
    - _self_destroy_counter: self-destruction counter
    """
    target: BoolExpr
    self_destroy: int
    _self_destroy_counter: int
    owner: Particle
    collsion_box_group = {}

    def __init__(self, info: dict[str, Union[str, float, int, Tuple]]) -> None:
        if called(self.__class__.__name__, info):
            return
        if "display_priority" not in info:
            info['display_priority'] = 1
        CollidableParticle.__init__(self, info)
        CollisionBox.collsion_box_group[self.id] = self
        attr = ["self_destroy", "_self_destroy_counter", 'owner']
        default = {
            'self_destroy': int(FPS // 2),
            '_self_destroy_counter': 0,
        }
        for key in default:
            if key not in info:
                info[key] = default[key]
        for item in attr:
            if item in info:
                setattr(self, item, info[item])
            else:
                raise InvalidConstructionInfo

    def count(self) -> None:
        self._self_destroy_counter += 1
        if self._self_destroy_counter >= self.self_destroy:
            self.remove()

    def sync(self):
        if isinstance(self.owner, Living):
            if self.owner.is_dead():
                self.remove()
        self.map_name = self.owner.map_name
        if isinstance(self.owner, Collidable):
            self.x = self.owner.x - 1 + self.owner.get_stat('diameter') / 2 - \
                     self.owner.get_stat('attack_range')
            self.y = self.owner.y - 1 + self.owner.get_stat('diameter') / 2 - \
                     self.owner.get_stat('attack_range')
        else:
            self.x = self.owner.x - self.owner.get_stat('attack_range')
            self.y = self.owner.y - self.owner.get_stat('attack_range')

    def remove(self):
        Particle.remove(self)
        CollisionBox.collsion_box_group.pop(self.id, None)

    def display(self, screen: pygame.Surface,
                location: Tuple[int, int]) -> None:
        screen.blit(self._texture, location)


class DirectionalParticle(CollidableParticle, Directional):
    """ Collidable particles that implements the directional interface """

    def __init__(self, info: dict[str, Union[str, float, int, Tuple]]) -> None:
        if called(self.__class__.__name__, info):
            return
        CollidableParticle.__init__(self, info)
        Directional.__init__(self, info)
        if self.texture not in Particle.rotation:
            Particle.rotation[self.texture] = {self.diameter: {}}
        else:
            Particle.rotation[self.texture][self.diameter] = {}

    def aim(self, obj: Positional) -> None:
        cx = self.x + self.diameter / 2 - 1
        cy = self.y + self.diameter / 2 - 1
        obj = (obj.x, obj.y)
        if isinstance(obj, Collidable):
            obj = (obj.x + obj.diameter / 2 - 1, obj.y + obj.diameter / 2 - 1)
        self.direction = get_direction((cx, cy), obj)

    def display(self, screen: pygame.Surface,
                location: Tuple[int, int]) -> None:
        radius = self.diameter / 2
        if self.direction not in Particle.rotation[self.texture][self.diameter]:
            Particle.rotation[self.texture][self.diameter][self.direction] = \
                pygame.transform.rotate(self._texture, self.direction)
        texture = Particle.rotation[self.texture][self.diameter][self.direction]
        centre_x = location[0] + radius - 1
        centre_y = location[1] + radius - 1
        size = texture.get_size()
        cx = centre_x - size[0] / 2 + radius
        cy = centre_y - size[1] / 2
        screen.blit(texture, [cx - radius, cy])

    def get_tile_in_contact(self) -> Particle:
        col = int((self.x - 1 + self.diameter / 2) // TILE_SIZE)
        row = int((self.y - 1 + self.diameter / 2) // TILE_SIZE)
        return self._surrounding_tiles[row][col]


class MovableParticle(DirectionalParticle, Movable):
    """ Directional particles that implements the movable interface
    """

    def __init__(self, info: dict[str, Union[str, float, int, Tuple]]) -> None:
        if called(self.__class__.__name__, info):
            return
        DirectionalParticle.__init__(self, info)

    def update_position(self) -> None:
        x_d = abs(self.get_stat('vx'))
        y_d = abs(self.get_stat('vy'))
        c_x = int(self.x)
        c_y = int(self.y)
        particles = []
        for row in self._surrounding_tiles:
            row = self._surrounding_tiles[row]
            for p in row:
                particles.append(row[p])
        particles += self.get_adjacent_entities(True)
        if self in particles:
            particles.remove(self)

        if self.get_stat('vx') == 0 and self.get_stat('vy') == 0:
            return
        if self.get_stat('vx') == 0:
            x_time = 0
            y_time = 1
        elif self.get_stat('vy') == 0:
            x_time = 1
            y_time = 0
        elif abs(self.get_stat('vx')) > abs(self.get_stat('vy')):
            x_time = int(round(abs(self.get_stat('vx')) / abs(self.get_stat(
                'vy')), 0))
            y_time = 1
        elif abs(self.get_stat('vx')) < abs(self.get_stat('vy')):
            x_time = 1
            y_time = int(round(abs(self.get_stat('vy')) / abs(self.get_stat(
                'vx')), 0))
        else:
            x_time, y_time = 1, 1

        while x_d > 0 or y_d > 0:
            for i in range(x_time):
                if x_d > 0:
                    if x_d >= 1:
                        value = self.get_stat('vx') / abs(self.get_stat('vx'))
                        x_d -= 1
                    else:
                        value = self.get_stat('vx') - int(self.get_stat('vx'))
                        x_d = 0
                    self.x += value
                    n_x = int(self.x)
                    if abs(n_x - c_x) >= 1:
                        for particle in particles:
                            #  particles are guaranteed to implement the
                            #  collidable interface
                            if particle.solid and self.solid \
                                    and self.detect_collision(particle):
                                self.x -= value
                                x_d = 0
                                break

            for i in range(y_time):
                if y_d > 0:
                    if y_d >= 1:
                        value = self.get_stat('vy') / abs(self.get_stat('vy'))
                        y_d -= 1
                    else:
                        value = self.get_stat('vy') - int(self.get_stat('vy'))
                        y_d = 0
                    self.y += value
                    n_y = int(self.y)
                    if abs(n_y - c_y) >= 1:
                        for particle in particles:
                            #  particles are guaranteed to implement the
                            #  collidable interface
                            if particle.solid and self.solid \
                                    and self.detect_collision(particle):
                                self.y -= value
                                y_d = 0
                                break


class Creature(MovableParticle, Living, Lightable):
    """
    Description: Movable particles that can act on its own

    Additional Attributes:
        light_on: Whether this creature is illuminating its surroundings
        active: Whether this creature is active
        color: Displayed color of this creature
    Representation Invariants:

    """
    creature_group = {}
    active: bool
    color: Tuple[int, int, int]
    light_on: bool

    def __init__(self, info: dict[str, Union[str, float, int, Tuple]]) -> None:
        if "display_priority" not in info:
            info['display_priority'] = 2

        if called(self.__class__.__name__, info):
            return
        DirectionalParticle.__init__(self, info)
        self._texture = pygame.transform.scale(
            Particle.textures[self.texture], (self.diameter * 2,
                                              self.diameter * 2))
        Movable.__init__(self, info)
        Lightable.__init__(self, info)
        Living.__init__(self, info)
        Creature.creature_group[self.id] = self
        attr = ["active", 'color', 'light_on']
        default = {
            'active': True,
            'color': (255, 255, 255),
            'light_on': True
        }
        for key in default:
            if key not in info:
                info[key] = default[key]
        for item in info:
            if item in attr:
                setattr(self, item, info[item])

    def display(self, screen: pygame.Surface,
                location: Tuple[int, int]) -> None:
        DirectionalParticle.display(self, screen, location)
        radius = self.diameter / 2
        if self.shape == CIRCLE:
            pygame.draw.circle(
                screen, self.color, (location[0] + self.diameter // 2, location[
                    1] + radius), radius)
        elif self.shape == SQUARE:
            pygame.draw.rect(
                screen, self.color, pygame.Rect(location[0] + radius, location[
                    1] + radius, radius, radius))

    def action(self, player_input: Optional[List[pygame.event.Event]]) -> None:
        """ AI of this creature, this method should
        be called on every active creature regularly
        """
        raise NotImplementedError

    def light(self):
        tile = self.get_tile_in_contact()
        assert isinstance(tile, Lightable)
        sl = self.get_stat('light_source')
        ol = tile.get_stat('light_source')
        if ol < sl:
            tile.add_stats({'light_source': sl - ol})

    def die(self):
        self.remove()

    def remove(self):
        Particle.remove(self)
        Creature.creature_group.pop(self.id, None)


class SweepAttackable(Creature, Attackable):

    def __init__(self, info: dict[str, Union[str, float, int]]) -> None:
        if called(self.__class__.__name__, info):
            return
        Creature.__init__(self, info)
        Attackable.__init__(self, info)

    def basic_attack(self, target=None) -> bool:
        """ Perform an attack and reset the attack counter """
        if self.can_attack():
            c1x = self.x - 1 + self.get_stat('diameter') / 2
            c1y = self.y - 1 + self.get_stat('diameter') / 2
            c2x = c1x - self.get_stat('attack_range')
            c2y = c1y - self.get_stat('attack_range')
            info = {
                'diameter': self.get_stat('attack_range') * 2 + 1,
                'shape': self.shape,
                'texture': 'attack_circle_64.png',
                'owner': self,
                'x': c2x,
                'y': c2y,
                'map_name': self.map_name
            }
            collision_box = CollisionBox(info)
            for entity in self.get_adjacent_entities(True):
                if not entity.id == self.id and isinstance(entity, Living):
                    if collision_box.detect_collision(entity):
                        entity.health -= self.get_stat('attack_power')
            self._attack_counter = 0
            return True
        return False


class Player(SweepAttackable):
    """
    Description: Player class

    Additional Attributes:
        pressed_keys: A list of pressed keys of this player

    Representation Invariants:

    """
    player_group = {}
    pressed_keys: List[int]
    mouse_buttons: Tuple[int, int, int]

    def __init__(self, info: dict[str, Union[str, float, int]]) -> None:
        if called(self.__class__.__name__, info):
            return
        SweepAttackable.__init__(self, info)
        Player.player_group[self.id] = self
        self.pressed_keys = []
        self.mouse_buttons = (0, 0, 0)

    def action(self, player_input: Optional[List[pygame.event.Event]]) -> None:
        self.mouse_buttons = pygame.mouse.get_pressed(3)
        for event in player_input:
            if event.type == pygame.KEYDOWN:
                if event.key not in self.pressed_keys:
                    self.pressed_keys.append(event.key)
            elif event.type == pygame.KEYUP:
                self.pressed_keys.remove(event.key)
        effective_directions = []
        for key in self.pressed_keys:
            if key == pygame.K_w or key == pygame.K_a:
                effective_directions.append(key)
            elif key == pygame.K_s:
                if pygame.K_w not in effective_directions:
                    effective_directions.append(key)
                else:
                    effective_directions.remove(pygame.K_w)
            elif key == pygame.K_d:
                if pygame.K_a not in effective_directions:
                    effective_directions.append(key)
                else:
                    effective_directions.remove(pygame.K_a)
        if pygame.K_w in effective_directions:
            if pygame.K_a in effective_directions:
                self.move(135)
            elif pygame.K_d in effective_directions:
                self.move(45)
            else:
                self.move(90)
        elif pygame.K_s in effective_directions:
            if pygame.K_a in effective_directions:
                self.move(225)
            elif pygame.K_d in effective_directions:
                self.move(315)
            else:
                self.move(270)
        elif pygame.K_a in effective_directions:
            self.move(180)
        elif pygame.K_d in effective_directions:
            self.move(0)

        # light

        # attack
        if self.mouse_buttons[0] == 1:
            self.perform_act('basic_attack')
        self.update_position()

    def remove(self):
        Creature.remove(self)
        Player.player_group.pop(self.id, None)


class Block(CollidableParticle, Lightable):
    """

    """
    block_group = {}

    def __init__(self, info: dict[str, Union[str, float, int]]) -> None:
        if called(self.__class__.__name__, info):
            return
        CollidableParticle.__init__(self, info)
        Lightable.__init__(self, info)
        Block.block_group[self.id] = self

    def remove(self):
        Particle.remove(self)
        Block.block_group.pop(self.id, None)

    def light(self):
        self.enlighten(self)
        if self.get_stat('brightness') > 0:
            blocks = self.get_adjacent_tiles()
            for block in blocks:
                assert isinstance(block, Block)
                if block.get_stat('brightness') < self.get_stat('brightness'):
                    self.enlighten(block)
                    block.light()


class NPC(SweepAttackable):
    """ Description: Non-Player Character class

    Additional Attributes:

    Representation Invariants:
    """
    npc_group = {}

    def __init__(self, info: dict[str, Union[str, float, int]]) -> None:
        if called(self.__class__.__name__, info):
            return
        SweepAttackable.__init__(self, info)
        NPC.npc_group[self.id] = self

    def query_info(self):
        pass

    def action(self, player_input: Optional[List[pygame.event.Event]]) -> None:
        if self.can_attack():
            self.perform_act('basic_attack')
        self.update_position()

    def remove(self):
        Creature.remove(self)
        NPC.npc_group.pop(self.id, None)
