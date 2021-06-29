import math
from typing import Tuple, Optional, List


def segment_intersection(l1: Tuple[Tuple[float, float], Tuple[float, float]],
                         l2: Tuple[Tuple[float, float], Tuple[float, float]]
                         ) -> Optional[Tuple[float, float]]:
    """ Return the intersection point of two line segments, none if they
     are not intersected.
    """
    # Calculate slopes and obtain line formula
    p1 = l1[0]
    p2 = l1[1]
    p3 = l2[0]
    p4 = l2[1]
    s1, s2, b1, b2 = None, None, None, None
    x, y = None, None
    if not p2[0] == p1[0]:
        s1 = (p2[1] - p1[1]) / (p2[0] - p1[0])
        b1 = p1[1] - s1 * p1[0]
    if not p3[0] == p4[0]:
        s2 = (p4[1] - p3[1]) / (p4[0] - p3[0])
        b2 = p3[1] - s2 * p3[0]
    if s1 is None and s2 is not None:
        x = p1[0]
        y = s2 * x + b2
    if s2 is None:
        x = p3[0]
        if s1 is None:
            if p3[0] == p1[0]:
                if p1[1] <= p3[1] <= p2[1] or p2[1] <= p3[1] <= p1[1]:
                    return x, p3[1]
                if p1[1] <= p4[1] <= p2[1] or p2[1] <= p4[1] <= p1[1]:
                    return x, p4[1]
                return None
            return None
        y = s1 * x + b1
    if s1 is not None and s2 is not None:
        if s1 == s2:
            a1 = pow(p1[0], 2) + pow(p1[1], 2)
            a2 = pow(p2[0], 2) + pow(p2[1], 2)
            a3 = pow(p3[0], 2) + pow(p3[1], 2)
            a4 = pow(p4[0], 2) + pow(p4[1], 2)
            if a1 <= a3 <= a2 or a2 <= a3 <= a1:
                return p3[0], p3[1]
            if a1 <= a4 <= a2 or a2 <= a4 <= a1:
                return p4[0], p4[1]
            return None
        x = (b2 - b1) / (s1 - s2)
        y = s1 * x + b1
    assert x is not None
    assert y is not None
    # Test if the point is on both line segment
    if point_on_segment(l1, (x, y)) and point_on_segment(l2, (x, y)):
        return x, y
    return None


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
    return min_x1 <= point[0] <= max_x1 and min_y1 <= point[1] <= max_y1


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
    >>> line3 = ()
    """
    p1 = l1[0]
    p2 = l1[1]
    if p1[0] == p2[0]:
        return p1[0] == point[0]
    if p2[1] == p1[1]:
        return p1[1] == point[1]
    slope = (p2[1] - p1[1]) / (p2[0] - p1[0])
    constant = p1[1] - slope * p1[0]
    y = slope * point[0] + constant
    return abs(y - point[1]) <= 0.00001


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
    centre = (circle_xy[0] + diameter / 2, circle_xy[1] + diameter / 2)

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
        return [(x, y)]
    x1 = (-b + math.sqrt(delta)) / (2 * a)
    x2 = (-b - math.sqrt(delta)) / (2 * a)
    v1 = pow(diameter / 2, 2) - pow((x1 - centre[0]), 2)
    v2 = pow(diameter / 2, 2) - pow((x2 - centre[0]), 2)
    y1 = math.sqrt(v1) + centre[1]
    y2 = -math.sqrt(v1) + centre[1]
    y3 = math.sqrt(v2) + centre[1]
    y4 = -math.sqrt(v2) + centre[1]
    if y1 == y2 and y3 == y4:
        points = [(x1, y1), (x2, y3)]
    else:
        points = [(x1, y1), (x1, y2), (x2, y3), (x2, y4)]
    returning = []
    for point in points:
        if point_on_line(l, point):
            returning.append(point)
    return returning

