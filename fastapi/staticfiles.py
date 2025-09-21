"""StaticFiles 대체 구현."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class StaticFiles:
    """정적 파일 디렉터리 경로만 저장한다."""

    directory: Path

    def __init__(self, *, directory: str | Path) -> None:
        self.directory = Path(directory)

