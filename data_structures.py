from typing import Any, List, Optional, Callable
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
    Description: A queue of items sorted by their priorities, items with higher priority will be popped first

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
        for i in self._items:
            if not self._comparator(item, i):
                self._items.insert(self._items.index(i), item)
                return
        self._items.append(item)

    def dequeue(self) -> Any:
        return self._items.pop()

    def is_empty(self) -> bool:
        return len(self._items) == 0