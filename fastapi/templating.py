"""Jinja2 템플릿을 대체하는 단순 렌더러."""

from __future__ import annotations

from pathlib import Path

from .responses import HTMLResponse


class Jinja2Templates:
    """템플릿 파일을 읽어 단순히 반환한다."""

    def __init__(self, *, directory: str) -> None:
        self.directory = Path(directory)

    def TemplateResponse(self, name: str, context: dict[str, object]) -> HTMLResponse:
        path = self.directory / name
        if path.exists():
            content = path.read_text(encoding="utf-8")
        else:  # pragma: no cover - 방어 코드
            content = ""
        return HTMLResponse(content)

