import heapq
import time
from typing import Tuple, Optional
from .models import ProcessedEmail

class PriorityEmailQueue:
    """
    Min-heap based on (-urgency_score, timestamp) so higher urgency pops first.
    """
    def __init__(self) -> None:
        self._heap: list[Tuple[int, float, str, ProcessedEmail]] = []

    def push(self, pemail: ProcessedEmail):
        # higher urgency → smaller negative value → pops first
        priority_key = -int(pemail.classification.urgency_score if pemail.classification else 5)
        heapq.heappush(self._heap, (priority_key, time.time(), pemail.record.id, pemail))

    def pop(self) -> Optional[ProcessedEmail]:
        if not self._heap:
            return None
        _, _, _, item = heapq.heappop(self._heap)
        return item

    def __len__(self):
        return len(self._heap)

email_queue = PriorityEmailQueue()
