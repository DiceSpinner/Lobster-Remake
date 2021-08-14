from typing import Any, List, Optional, Callable, Tuple
from error import EmptyStackError


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
    _items: Items stored in this queue. The first item is being represented by
    the first item in the list.
    """
    _items: List

    def __init__(self) -> None:
        """Initialize a new empty queue."""
        self._items = []

    def is_empty(self) -> bool:
        """Return whether this queue contains no items.

        >>> q = Queue()
        >>> q.is_empty()
        True
        >>> q.enqueue('1')
        >>> q.is_empty()
        False
        """
        return self._items == []

    def enqueue(self, item: Any) -> None:
        """Add <item> to the back of this queue.
        """
        self._items.append(item)

    def dequeue(self) -> Optional[Any]:
        """Remove and return the item at the front of this queue.

        Return None if this Queue is empty.

        >>> q = Queue()
        >>> q.enqueue('1')
        >>> q.enqueue('2')
        >>> q.dequeue()
        '1'
        """
        if self.is_empty():
            return None
        else:
            return self._items.pop(0)


class PriorityQueue:
    """
    Description: A queue of items sorted by their priorities, items with higher
    priority will be popped first
    === Private attributes ===
    _items: Items stored in this queue. The first item is being represented by
    the first item in the list.
    _comparator: The callable function used to sort items
    """
    _items: List[Any]
    _comparator: Callable[[Any, Any], bool]

    def __init__(self, comparator: Callable) -> None:
        self._comparator = comparator
        self._items = []

    def enqueue(self, item: Any) -> None:
        for i in range(len(self._items)):
            it = self._items[i]
            if self._comparator(item, it):
                self._items.insert(i, item)
                return
        self._items.append(item)

    def dequeue(self) -> Any:
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
    the first item in the list.
    _pointer: Index of the item being popped
    _comparator: The callable function used to sort items
    _size: Size of the queue
    _weights: A dictionary that contains the weight factors of all of the items
        in this queue.
    _popped_keys: A list of keys that has been popped out
    _counter: A number that represents an unoccupied key
    """

    _items: List[Tuple[int, Any]]
    _weights: dict[int, int]
    _comparator: Callable[[Any, Any], bool]
    _pointer: int
    _size: int
    _popped_keys: List[int]
    _counter: int

    def __init__(self, comparator: Callable) -> None:
        self._comparator = comparator
        self._items = []
        self._size = 0
        self._pointer = 0
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
        [('item', 2), ('item', 1)]
        >>> queue = WeightedPriorityQueue(_num_comparator)
        >>> queue.enqueue(10, 1)
        0
        >>> queue.enqueue(20, 1)
        1
        >>> print(queue)
        [(20, 1), (10, 1)]
        """
        num = self._counter
        for i in range(len(self._items)):
            it = self._items[i][1]
            if self._comparator(item, it):
                self._items.insert(i, (num, item))
                self._weights[num] = weight
                self._size += 1
                self._counter += 1
                return num
        self._counter += 1
        self._weights[num] = weight
        self._items.append((num, item))
        self._size += 1
        return num

    def dequeue(self) -> Any:
        """ Pop items from the queue
        >>> queue = WeightedPriorityQueue(_num_comparator)
        >>> queue.enqueue(10, 1)
        0
        >>> queue.enqueue(20, 3)
        1
        >>> print(queue)
        [(20, 3), (10, 1)]
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
            item = self._items[self._pointer]
            weight = self._weights[item[0]] - 1
            if weight <= 0:
                self._items.pop(self._pointer)
                self._size -= 1
                self._weights.pop(item[0], None)
                if self._pointer >= self._size:
                    self._pointer = 0
                return item[1]
            self._weights[item[0]] = weight
            if self._pointer == self._size - 1:
                # reset the pointer
                self._pointer = 0
            else:
                self._pointer += 1
            return item[1]

    def reset(self):
        """ Reset the pointer to its initial position """
        self._pointer = 0

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
        [(20, 1), (10, 1)]
        >>> queue.set_weight(0, 3)
        >>> print(queue)
        [(20, 1), (10, 3)]
        >>> queue.set_weight(1, 2)
        >>> print(queue)
        [(20, 2), (10, 3)]
        """
        self._weights[key] = weight


def _test_comparator(i1: Any, i2: Any) -> bool:
    return True


def _num_comparator(i1: int, i2: int) -> bool:
    return i1 > i2
