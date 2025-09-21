"""필수 Response 타입에 대한 간단한 구현."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class HTMLResponse:
    """HTML 문자열을 표현하는 응답."""

    content: str
    status_code: int = 200
    media_type: str = "text/html; charset=utf-8"

    def __str__(self) -> str:  # pragma: no cover - 디버깅 편의용
        return self.content

