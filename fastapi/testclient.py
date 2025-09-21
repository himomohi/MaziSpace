"""테스트 전용 TestClient 구현."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from . import FastAPI, HTTPException


@dataclass(slots=True)
class Response:
    """테스트 클라이언트 응답 객체."""

    status_code: int
    _json_data: Any = None
    text: str = ""

    def json(self) -> Any:
        if self._json_data is None:  # pragma: no cover - HTML 응답 방어
            raise ValueError("JSON 데이터가 없습니다.")
        return self._json_data


class TestClient:
    """FastAPI 호환 테스트 클라이언트."""

    def __init__(self, app: FastAPI) -> None:
        self.app = app

    def _build_response(self, status_code: int, data: Any) -> Response:
        if hasattr(data, "content") and hasattr(data, "status_code"):
            return Response(status_code=int(data.status_code), _json_data=None, text=str(data.content))
        return Response(status_code=status_code, _json_data=data)

    def _request(self, method: str, path: str, json: Any = None) -> Response:
        try:
            status_code, result = self.app._handle_request(method, path, json)
        except HTTPException as exc:
            return Response(status_code=exc.status_code, _json_data={"detail": exc.detail})
        return self._build_response(status_code, result)

    def get(self, path: str) -> Response:
        return self._request("GET", path)

    def post(self, path: str, *, json: Any = None) -> Response:
        return self._request("POST", path, json=json)

