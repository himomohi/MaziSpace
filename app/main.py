"""FastAPI 기반 모던 웹 게임 애플리케이션."""

from __future__ import annotations

from pathlib import Path
from typing import List

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field

from .game import Leaderboard, leaderboard

BASE_DIR = Path(__file__).resolve().parent.parent
TEMPLATE_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"


def create_app(board: Leaderboard | None = None) -> FastAPI:
    """FastAPI 애플리케이션을 생성한다."""

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

    class ScorePayload(BaseModel):
        player_name: str = Field(..., max_length=32, examples=["NovaPilot"])
        score: int = Field(..., ge=0, examples=[1280])

    class ScoreResponse(BaseModel):
        player_name: str
        score: int

    @app.get("/", response_class=HTMLResponse)
    async def index(request: Request) -> HTMLResponse:
        return templates.TemplateResponse("index.html", {"request": request})

    @app.get("/api/leaderboard", response_model=List[ScoreResponse])
    async def read_leaderboard() -> List[ScoreResponse]:
        entries = await board.entries()
        return [ScoreResponse(player_name=item.player_name, score=item.score) for item in entries]

    @app.post(
        "/api/leaderboard",
        response_model=List[ScoreResponse],
        status_code=status.HTTP_201_CREATED,
    )
    async def submit_score(payload: ScorePayload) -> List[ScoreResponse]:
        try:
            entries = await board.submit(player_name=payload.player_name, score=payload.score)
        except ValueError as exc:  # pragma: no cover - 방어적 예외 처리
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

        return [ScoreResponse(player_name=item.player_name, score=item.score) for item in entries]

    return app


app = create_app()
"""배포 시 사용되는 기본 FastAPI 애플리케이션."""
