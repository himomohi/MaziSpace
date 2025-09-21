"""게임 로직과 리더보드 관리를 담당하는 모듈."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import List


@dataclass(frozen=True, slots=True)
class ScoreEntry:
    """리더보드에 노출되는 점수 항목."""

    player_name: str
    score: int


class Leaderboard:
    """게임 점수 리더보드를 관리하는 클래스."""

    def __init__(self, max_entries: int = 10) -> None:
        self.max_entries = max_entries
        self._entries: list[ScoreEntry] = []
        self._lock = asyncio.Lock()

    async def submit(self, player_name: str, score: int) -> List[ScoreEntry]:
        """새로운 점수를 등록하고 현재 리더보드를 반환한다."""

        if score < 0:
            raise ValueError("점수는 0 이상이어야 합니다.")

        normalized_name = player_name.strip() or "무명 파일럿"

        async with self._lock:
            entry = ScoreEntry(player_name=normalized_name[:32], score=score)
            self._entries.append(entry)
            self._entries.sort(key=lambda item: item.score, reverse=True)
            self._entries = self._entries[: self.max_entries]
            return list(self._entries)

    async def entries(self) -> List[ScoreEntry]:
        """현재 리더보드 목록을 반환한다."""

        async with self._lock:
            return list(self._entries)

    async def clear(self) -> None:
        """테스트나 초기화를 위해 리더보드를 비운다."""

        async with self._lock:
            self._entries.clear()


leaderboard = Leaderboard()
"""애플리케이션 전역에서 공유되는 기본 리더보드 인스턴스."""
