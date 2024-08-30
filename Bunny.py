import math


def solution(l):
    # Your code here
    lst = all_perm(l)
    m = -math.inf
    for perm in lst:
        if perm % 3 == 0 and perm > m:
            m = perm
    if not m == -math.inf:
        return m
    return 0


def permutation(elements, to_int=False):
    if len(elements) <= 1:
        return [elements]
    p = permutation(elements[1:])
    result = []
    for perm in p:
        for i in range(len(elements)):
            # nb elements[0:1] works in both string and list contexts
            if to_int:
                result.append(int(perm[:i] + elements[0] + perm[i:]))
            else:
                result.append(perm[:i] + elements[0] + perm[i:])
    return result


def all_perm(elements):
    if len(elements) <= 1:
        return [concat(elements)]
    result = permutation(stringify(elements), True)
    for i in range(len(elements)):
        lst = list(elements)
        lst.pop(i)
        result.extend(all_perm(lst))
    return result


def stringify(elements):
    result = ""
    for i in elements:
        result += str(i)
    return result


def concat(elements):
    result = ""
    for i in elements:
        result += str(i)
    return int(result)


print(solution([3, 1, 4, 1, 5, 9]))
