import math
from typing import Tuple, Optional, List, Union


def float_equality(v1: float, v2: float, precision=0) -> bool:
    """ Return true of two floats are equal """
    p = pow(0.1, precision)
    return abs(v1 - v2) < p


def segment_intersection(l1: Tuple[Tuple[float, float], Tuple[float, float]],
                         l2: Tuple[Tuple[float, float], Tuple[float, float]]
                         ) -> Optional[Union[Tuple[float, float],
                                             Tuple[Tuple[float, float], Tuple[
                                                 float, float]]]]:
    """ Return the intersection point of two line segments, none if they
     are not intersected. Return a line segment if there's infinite POI.
    """
    # Calculate slopes and obtain line formula
    i1 = calculate_slope_constant(l1[0], l1[1])
    i2 = calculate_slope_constant(l2[0], l2[1])
    print("Lines:", l1, l2)
    print("Slopes:", i1, i2)
    if i1 is None:
        if i2 is None:
            if l1[0][0] == l2[0][0]:
                y1, y2, y3, y4 = l1[0][1], l1[1][1], l2[0][1], l2[1][1]
                max_y = max(y1, y2, y3, y4)
                min_y = min(y1, y2, y3, y4)
                pool = [l1[0], l1[1], l2[0], l2[1]]
                returning = []
                for i in range(len(pool)):
                    y = pool[i][1]
                    if not y == min_y and not y == max_y:
                        returning.append(y)
                return returning[0], returning[1]
            return None
        x = l1[0][0]
        y = i2[0] * x + i2[1]
        print("Attempting 2", x, y)
        if point_on_segment(l1, (x, y)) and point_on_segment(l2, (x, y)):
            return x, y
        return None
    if i2 is None:
        x = l2[0][0]
        y = i1[0] * x + i1[1]
        print("Attempting 3", x, y)
        if point_on_segment(l1, (x, y)) and point_on_segment(l2, (x, y)):
            return x, y
        return None
    if i1[0] == i2[0]:
        return None
    if i1[0] == i2[0]:
        x1, x2, x3, x4 = l1[0][0], l1[1][0], l2[0][0], l2[1][0]
        max_x = max(x1, x2, x3, x4)
        min_x = min(x1, x2, x3, x4)
        pool = [l1[0], l1[1], l2[0], l2[1]]
        returning = []
        for i in range(len(pool)):
            x = pool[i][1]
            if not x == min_x and not x == max_x:
                returning.append(x)
        return returning[0], returning[1]
    x = (i2[1] - i1[1]) / (i1[0] - i2[0])
    y = i1[0] * x + i1[1]
    print("Attempting 4", x, y)
    if point_on_segment(l1, (x, y)) and point_on_segment(l2, (x, y)):
        return x, y
    return None


def calculate_slope_constant(p1: Tuple[float, float],
                             p2: Tuple[float, float]) -> Optional[
        Union[Tuple[float, float], int]]:
    """ Calculate the slope/constant of the given line,
    return None if it's vertical
    """
    if p1[0] == p2[0]:
        return None
    if p1[1] == p2[1]:
        return 0, p1[1]
    slope = (p2[1] - p1[1]) / (p2[0] - p1[0])
    constant = p1[1] - p1[0] * slope
    return slope, constant


def point_on_segment(l1: Tuple[Tuple[float, float], Tuple[float, float]],
                     point: Tuple[float, float]
                     ) -> bool:
    """ Test if the point is on the given line segment """
    p1 = l1[0]
    p2 = l1[1]
    min_x1 = min(p1[0], p2[0])
    max_x1 = max(p1[0], p2[0])
    min_y1 = min(p1[1], p2[1])
    max_y1 = max(p1[1], p2[1])
    return (min_x1 < point[0] < max_x1 or float_equality(point[0], min_x1)
            or float_equality(point[0], max_x1)
            ) and (min_y1 < point[1] < max_y1 or
                   (float_equality(point[1], min_y1) or
                    float_equality(point[1], max_y1)))


def point_on_line(l1: Tuple[Tuple[float, float], Tuple[float, float]],
                  point: Tuple[float, float]
                  ) -> bool:
    """ Test if the point is on the given line

    >>> line = ((0, 2), (0, 3))
    >>> p = (1, 2)
    >>> point_on_line(line, p)
    False
    >>> line2 = ((0, 1), (3, 4))
    >>> point_on_line(line2, p)
    True
    >>> line3 = ((0, 4), (2, 0))
    >>> point2 = (-1, 6)
    >>> point_on_line(line3, point2)
    True
    """
    p1 = l1[0]
    p2 = l1[1]
    if abs(p1[0] - p2[0]) <= 0.0001:
        return abs(p1[0] - point[0]) <= 0.0001
    if abs(p2[1] - p1[1]) <= 0.0001:
        return abs(p1[1] - point[1]) <= 0.0001
    slope = (p2[1] - p1[1]) / (p2[0] - p1[0])
    constant = p1[1] - slope * p1[0]
    y = slope * point[0] + constant
    return abs(y - point[1]) <= 0.0001


def line_circle_intersection(l: Tuple[Tuple[float, float], Tuple[float, float]],
                             circle_xy: Tuple[float, float], diameter: int
                             ) -> Optional[List[Tuple[float, float]]]:
    """ Return points of intersection of the circle and the line
    Return None if there's none

    >>> line = ((0, 2), (1, 2))
    >>> circle = (-1, 0)
    >>> d = 4
    >>> line_circle_intersection(line, circle, d)
    [(3.0, 2.0), (-1.0, 2.0)]
    >>> line2 = ((0, 1), (1, 4))
    >>> line_circle_intersection(line2, circle, d)
    [(1.0, 4.0), (-0.2, 0.4)]
    >>> line3 = ((0, 4), (2, 0))
    >>> line_circle_intersection(line3, circle, d)
    [(0.106, 3.789), (1.894, 0.211)]
    """

    # formula of the circle: r^2 = (x - h)^2 + (y - k)^2
    # centre of the circle
    centre = (circle_xy[0] + diameter / 2 - 0.5,
              circle_xy[1] + diameter / 2 - 0.5)

    # Slope of the line
    p1 = l[0]
    p2 = l[1]
    if p1[0] == p2[0]:
        x = p1[0]
        value = pow(diameter / 2, 2) - pow((x - centre[0]), 2)
        if value < 0:
            return None
        y1 = math.sqrt(value) + centre[1]
        y2 = -math.sqrt(value) + centre[1]
        if y1 == y2:
            return [(x, y1)]
        return [(x, y1), (x, y2)]
    slope = (p2[1] - p1[1]) / (p2[0] - p1[0])
    constant = p1[1] - slope * p1[0]
    # solve quadratic
    a = pow(slope, 2) + 1
    b = 2 * slope * (constant - centre[1]) - 2 * centre[0]
    c = pow(constant - centre[1], 2) - pow(diameter / 2, 2) + pow(centre[0], 2)
    delta = pow(b, 2) - 4 * a * c
    if delta < 0:
        return None
    elif delta == 0:
        x = (-b) / (2 * a)
        value = pow(diameter / 2, 2) - pow((x - centre[0]), 2)
        y = math.sqrt(value) + centre[1]
        return [(round(x, 0), round(y, 0))]
    x1 = (-b + math.sqrt(delta)) / (2 * a)
    x2 = (-b - math.sqrt(delta)) / (2 * a)
    v1 = pow(diameter / 2, 2) - pow((x1 - centre[0]), 2)
    v2 = pow(diameter / 2, 2) - pow((x2 - centre[0]), 2)
    y1 = math.sqrt(v1) + centre[1]
    y2 = -math.sqrt(v1) + centre[1]
    y3 = math.sqrt(v2) + centre[1]
    y4 = -math.sqrt(v2) + centre[1]
    # rounding
    if y1 == y2 and y3 == y4:
        points = [(x1, y1), (x2, y3)]
    else:
        points = [(x1, y1), (x1, y2), (x2, y3), (x2, y4)]
    returning = []
    for point in points:
        if point_on_line(l, point):
            returning.append(point)
    return returning


def point_vec_left(
        l1: Tuple[Tuple[float, float], Tuple[float, float]],
        point: Tuple[float, float]) -> bool:
    """ Test if the point is on the left side of given vector

    Assume l1[0] is the starting point
    """
    p1 = l1[0]
    p2 = l1[1]

    if p1[1] == p2[1]:
        if p1[0] < p2[0]:
            return point[1] < p1[1]
        return point[1] > p1[1]
    if p1[0] == p2[0]:
        if p1[1] < p2[1]:
            return point[0] > p1[0]
        return point[0] < p1[0]
    slope = (p2[1] - p1[1]) / (p2[0] - p1[0])
    constant = p1[1] - slope * p1[0]
    y_on_line = slope * point[0] + constant
    if p1[0] < p2[0]:
        return y_on_line < point[1]
    return y_on_line > point[1]


def point_vec_right(
        l1: Tuple[Tuple[float, float], Tuple[float, float]],
        point: Tuple[float, float]) -> bool:
    """ Test if the point is on the right side of given vector

    Assume l1[0] is the starting point
    """
    p1 = l1[0]
    p2 = l1[1]
    if p1[1] == p2[1]:
        if p1[0] < p2[0]:
            return point[1] > p1[1]
        return point[1] < p1[1]
    if p1[0] == p2[0]:
        if p1[1] < p2[1]:
            return point[0] < p1[0]
        return point[0] > p1[0]
    slope = (p2[1] - p1[1]) / (p2[0] - p1[0])
    constant = p1[1] - slope * p1[0]
    y_on_line = slope * point[0] + constant
    if p1[0] < p2[0]:
        return y_on_line > point[1]
    return y_on_line < point[1]
