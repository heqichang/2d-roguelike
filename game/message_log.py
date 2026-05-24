from __future__ import annotations

from typing import List, Tuple


class MessageLog:
    def __init__(self, max_messages: int = 100):
        self.messages: List[Tuple[str, Tuple[int, int, int]]] = []
        self.max_messages = max_messages

    def add(self, text: str, color: Tuple[int, int, int] = (255, 255, 255)) -> None:
        self.messages.append((text, color))
        if len(self.messages) > self.max_messages:
            self.messages.pop(0)

    def get_recent(self, count: int = 10) -> List[Tuple[str, Tuple[int, int, int]]]:
        return self.messages[-count:]

    def clear(self) -> None:
        self.messages.clear()
