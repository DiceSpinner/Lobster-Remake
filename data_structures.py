from typing import Any, List, Callable, Tuple
from error import EmptyStackError
from functools import cmp_to_key
from bisect import bisect_right
from collections import deque


# Stack
class Stack:
    """
    Description: A last-in-first-out (LIFO) stack of items.

    === Private Attributes ===
    _items:
        Items being stored in this stack, the top of the stack is being
        represented by the last item in the list.
    """
    _items: List

    def __init__(self) -> None:
        """Initialize a new empty stack."""
        self._items = []

    def is_empty(self) -> bool:
        """Return whether this stack is empty.

        >>> s = Stack()
        >>> s.is_empty()
        True
        >>> s.push('1')
        >>> s.is_empty()
        False
        """
        return len(self._items) == 0

    def push(self, item: Any) -> None:
        """Add a new element to the top of this stack."""
        self._items.append(item)

    def pop(self) -> Any:
        """Remove and return the element at the top of this stack.

        Raise an EmptyStackError if this stack is empty.

        >>> s = Stack()
        >>> s.push('1')
        >>> s.push('2')
        >>> s.pop()
        '2'
        """
        if self.is_empty():
            raise EmptyStackError
        else:
            return self._items.pop()


# Queue
class Queue:
    """
    Description: A first-in-first-out (FIFO) queue of items.

    === Private attributes ===
    _items: Items stored in this queue.
    """
    _items: deque

    def __init__(self) -> None:
        """Initialize a new empty queue."""
        self._items = deque()

    def is_empty(self) -> bool:
        """Return whether this queue contains no items.

        >>> q = Queue()
        >>> q.is_empty()
        True
        >>> q.enqueue('1')
        >>> q.is_empty()
        False
        """
        return len(self._items) == 0

    def enqueue(self, item: Any) -> None:
        """Add <item> to the back of this queue.
        """
        self._items.append(item)

    def dequeue(self) -> Any:
        """Remove and return the item at the front of this queue.

        Return None if this Queue is empty.

        >>> q = Queue()
        >>> q.enqueue('1')
        >>> q.enqueue('2')
        >>> q.dequeue()
        '1'
        """
        return self._items.popleft()


class PriorityQueue:
    """
    Description: A queue of items sorted by their priorities, items with higher
    priority will be popped first

    === Private attributes ===
    _items: Items stored in this queue. The first item is being represented by
    the last item in the list.
    _higher_priority: The callable function used to sort items
    """
    _items: List[Any]
    _higher_priority: Callable[[Any, Any], bool]
    _key_func: Callable[[Any], Any]
    _keys: List[Any]

    def __init__(self, comparator: Callable) -> None:
        self._higher_priority = comparator
        self._items = []
        self._key_func = cmp_to_key(comparator)
        self._keys = []

    def enqueue(self, item: Any) -> None:
        key = self._key_func(item)
        index = bisect_right(self._keys, key)
        self._keys.insert(index, key)
        self._items.insert(index, item)

    def dequeue(self) -> Any:
        self._keys.pop()
        return self._items.pop()

    def is_empty(self) -> bool:
        return len(self._items) == 0


class WeightedPriorityQueue:
    """
    Description: A queue of items sorted by their priorities, items with higher
    priority will be popped first. Additionally, each item has a weight factor
    assigned to it. Popping items will cause their weight factor to drop by 1.
    The item will not be fully removed from the queue if the weight factor is
    greater than 0. Enqueuing an item returns the key to access the weight
    factor of that item. This can be used to modify its weight factor.

    === Private attributes ===
    _items: Items stored in this queue. The first item is being represented by
    the last item in the list.
    _pointer: Index of the item being popped
    _higher_priority: The callable function used to sort items
    _size: Size of the queue
    _weights: A dictionary that contains the weight factors of all of the items
        in this queue.
    _popped_keys: A list of keys that has been popped out
    _counter: A number that represents an unoccupied key
    """

    _items: List[Tuple[int, Any]]
    _weights: dict[int, int]
    _higher_priority: Callable[[Any, Any], bool]
    _key_func: Callable[[Any], Any]
    _keys: List[Any]
    _pointer: int
    _size: int
    _popped_keys: List[int]
    _counter: int

    def __init__(self, comparator: Callable) -> None:
        self._higher_priority = comparator
        self._key_func = cmp_to_key(comparator)
        self._keys = []
        self._items = []
        self._size = 0
        self._pointer = -1
        self._weights = {}
        self._popped_keys = []
        self._counter = 0

    def __str__(self):
        string = "["
        for item in self._items:
            key = item[0]
            item = item[1]
            weight = self._weights[key]
            if isinstance(item, str):
                s = "'" + item + "'"
            else:
                s = str(item)
            string += "(" + s + ", " + str(weight) + "), "
        return string[:-2] + "]"

    def enqueue(self, item: Any, weight: int) -> int:
        """  Enqueue the item with the given weight and returns the key that can
         be used to access its weight factor

        >>> queue = WeightedPriorityQueue(_test_comparator)
        >>> queue.enqueue("item", 1)
        0
        >>> print(queue)
        [('item', 1)]
        >>> queue.enqueue("item", 2)
        1
        >>> print(queue)
        [('item', 1), ('item', 2)]
        >>> queue = WeightedPriorityQueue(_num_comparator)
        >>> queue.enqueue(10, 1)
        0
        >>> queue.enqueue(20, 1)
        1
        >>> print(queue)
        [(10, 1), (20, 1)]
        >>> queue.enqueue(30, 1)
        2
        >>> print(queue)
        [(10, 1), (20, 1), (30, 1)]
        >>> queue.enqueue(5, 1)
        3
        >>> print(queue)
        [(5, 1), (10, 1), (20, 1), (30, 1)]
        """
        key = self._assign_key()
        item_key = self._key_func(item)
        index = bisect_right(self._keys, item_key)
        self._items.insert(index, (key, item))
        self._keys.insert(index, item_key)
        self._weights[key] = weight
        self._size += 1

        return key

    def _assign_key(self) -> int:
        try:
            return self._popped_keys.pop()
        except IndexError:
            num = self._counter
            self._counter += 1
            return num

    def dequeue(self) -> Any:
        """ Pop items from the queue

        Key-note: Items with 0 weight before popping will be removed from the
            queue without returning, when this happens, the next item in the
            queue will be returned.

        >>> queue = WeightedPriorityQueue(_num_comparator)
        >>> queue.enqueue(10, 1)
        0
        >>> queue.enqueue(20, 3)
        1
        >>> print(queue)
        [(10, 1), (20, 3)]
        >>> queue.dequeue()
        20
        >>> queue.dequeue()
        10
        >>> print(queue)
        [(20, 2)]
        >>> queue.dequeue()
        20
        >>> queue.dequeue()
        20
        >>> queue.is_empty()
        True
        """
        if self._size > 0:
            key, item = self._items[self._pointer]
            weight = self._weights[key] - 1
            if weight == 0:
                self._items.pop(self._pointer)
                self._size -= 1
                self._weights.pop(key, None)
                self._keys.pop(self._pointer)
                self._popped_keys.append(key)
                if self._pointer < -self._size:
                    self._pointer = -1
                return item
            if weight < 0:
                self._items.pop(self._pointer)
                self._size -= 1
                self._pointer -= 1
                return self.dequeue()
            self._weights[key] = weight
            if self._pointer == -self._size:
                # reset the pointer
                self._pointer = -1
            else:
                self._pointer -= 1
            return item

    def reset(self):
        """ Reset the pointer to its initial position """
        self._pointer = -1

    def is_empty(self) -> bool:
        return self._size == 0

    def get_size(self):
        return self._size

    def set_weight(self, key: int, weight: int) -> None:
        """ Set the weight of the given item

        >>> queue = WeightedPriorityQueue(_num_comparator)
        >>> queue.enqueue(10, 1)
        0
        >>> queue.enqueue(20, 1)
        1
        >>> print(queue)
        [(10, 1), (20, 1)]
        >>> queue.set_weight(0, 3)
        >>> print(queue)
        [(10, 3), (20, 1)]
        >>> queue.set_weight(1, 2)
        >>> print(queue)
        [(10, 3), (20, 2)]
        """
        try:
            self._weights[key] = weight
            if weight == 0:
                self._size -= 1
        except KeyError:
            pass

    def get_weight(self, key: int) -> int:
        return self._weights[key]


def _test_comparator(i1: Any, i2: Any) -> int:
    return 1


def _num_comparator(i1: int, i2: int) -> int:
    return i1 - i2
