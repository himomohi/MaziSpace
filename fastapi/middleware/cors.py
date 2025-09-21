"""CORS 미들웨어에 대한 최소 대체 구현."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence


@dataclass(slots=True)
class CORSMiddleware:
    """테스트에서 필요한 설정 정보를 저장한다."""

    allow_origins: Sequence[str] | None = None
    allow_credentials: bool = False
    allow_methods: Sequence[str] | None = None
    allow_headers: Sequence[str] | None = None

    def __init__(
        self,
        *,
        allow_origins: Sequence[str] | None = None,
        allow_credentials: bool = False,
        allow_methods: Sequence[str] | None = None,
        allow_headers: Sequence[str] | None = None,
    ) -> None:
        self.allow_origins = tuple(allow_origins or [])
        self.allow_credentials = bool(allow_credentials)
        self.allow_methods = tuple(allow_methods or [])
        self.allow_headers = tuple(allow_headers or [])

