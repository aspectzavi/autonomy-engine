"""
Task queue.

Provides priority-aware storage for executable tasks.
"""

from __future__ import annotations

from collections.abc import Iterator
from heapq import heappop, heappush
from itertools import count

from backend.core.tasks.task import Task


class TaskQueue:
    """
    Priority-aware task queue.

    Higher-priority tasks are dequeued before lower-priority tasks.
    Tasks with equal priority preserve FIFO ordering.
    """

    def __init__(self) -> None:
        self._queue: list[tuple[int, int, Task]] = []
        self._sequence = count()

    # ------------------------------------------------------------------
    # Queue Operations
    # ------------------------------------------------------------------

    def enqueue(
        self,
        task: Task,
    ) -> None:
        """
        Add a task to the queue.
        """
        heappush(
            self._queue,
            (
                -int(task.priority),
                next(self._sequence),
                task,
            ),
        )

    def dequeue(self) -> Task:
        """
        Remove and return the next task.

        Raises:
            IndexError:
                If the queue is empty.
        """
        _, _, task = heappop(self._queue)
        return task

    def peek(self) -> Task:
        """
        Return the next task without removing it.

        Raises:
            IndexError:
                If the queue is empty.
        """
        _, _, task = self._queue[0]
        return task

    def clear(self) -> None:
        """
        Remove all queued tasks.
        """
        self._queue.clear()

    # ------------------------------------------------------------------
    # Inspection
    # ------------------------------------------------------------------

    @property
    def empty(self) -> bool:
        """
        Whether the queue is empty.
        """
        return not self._queue

    def __len__(self) -> int:
        """
        Number of queued tasks.
        """
        return len(self._queue)

    def __iter__(self) -> Iterator[Task]:
        """
        Iterate over queued tasks.

        Iteration order reflects the current queue ordering.
        """
        for _, _, task in sorted(self._queue):
            yield task

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def diagnostics(self) -> dict[str, object]:
        """
        Return queue diagnostics.
        """
        return {
            "size": len(self),
            "empty": self.empty,
            "tasks": [
                task.diagnostics()
                for task in self
            ],
        }