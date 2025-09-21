"""FastAPI 스타일 인터페이스를 갖춘 경량 웹 애플리케이션."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .game import Leaderboard, leaderboard

BASE_DIR = Path(__file__).resolve().parent.parent
TEMPLATE_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"


def _serialize_entries(entries: Iterable) -> list[dict[str, int | str]]:
    return [
        {"player_name": item.player_name, "score": item.score}
        for item in entries
    ]


def _validate_payload(payload: object) -> tuple[str, int]:
    if not isinstance(payload, dict):
        raise ValueError("요청 본문은 JSON 객체여야 합니다.")

    name = payload.get("player_name")
    score = payload.get("score")

    if not isinstance(name, str) or not name.strip():
        raise ValueError("플레이어 이름은 공백이 아닌 문자열이어야 합니다.")

    if not isinstance(score, int):
        raise ValueError("점수는 정수여야 합니다.")

    return name, score


def create_app(board: Leaderboard | None = None) -> FastAPI:
    """FastAPI 호환 애플리케이션을 생성한다."""

    app = FastAPI(title="MaziSpace", description="스페이스 러너 웹 게임", version="0.1.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    static_mount = StaticFiles(directory=STATIC_DIR)
    app.mount("/static", static_mount, name="static")

    templates = Jinja2Templates(directory=str(TEMPLATE_DIR))
    board = board or leaderboard

    @app.get("/", response_class=HTMLResponse)
    async def index(request: Request) -> HTMLResponse:
        return templates.TemplateResponse("index.html", {"request": request})

    @app.get("/api/leaderboard")
    async def read_leaderboard() -> list[dict[str, int | str]]:
        entries = await board.entries()
        return _serialize_entries(entries)

    @app.post("/api/leaderboard", status_code=status.HTTP_201_CREATED)
    async def submit_score(payload: dict[str, object] | None = None) -> list[dict[str, int | str]]:
        try:
            player_name, score = _validate_payload(payload or {})
            entries = await board.submit(player_name=player_name, score=score)
        except ValueError as exc:  # pragma: no cover - 방어적 예외 처리
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

        return _serialize_entries(entries)

    return app


app = create_app()
"""배포 시 사용되는 기본 FastAPI 애플리케이션."""
