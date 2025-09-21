"""테스트 환경을 위한 최소 FastAPI 대체 구현."""

from __future__ import annotations

import asyncio
import inspect
from dataclasses import dataclass
from http import HTTPStatus
from typing import Any, Callable, Dict, Iterable, Optional


__all__ = [
    "FastAPI",
    "HTTPException",
    "Request",
    "status",
]


class HTTPException(Exception):
    """HTTP 오류 응답을 표현하기 위한 예외."""

    def __init__(self, status_code: int, detail: str) -> None:
        self.status_code = int(status_code)
        self.detail = detail
        super().__init__(detail)


@dataclass(slots=True)
class Request:
    """라우트 핸들러에 전달되는 최소 요청 객체."""

    scope: Dict[str, Any] | None = None


class status:
    """테스트에 필요한 HTTP 상태 코드 상수."""

    HTTP_200_OK = HTTPStatus.OK.value
    HTTP_201_CREATED = HTTPStatus.CREATED.value
    HTTP_400_BAD_REQUEST = HTTPStatus.BAD_REQUEST.value
    HTTP_404_NOT_FOUND = HTTPStatus.NOT_FOUND.value


class Route:
    """FastAPI 스타일 라우트 메타데이터."""

    def __init__(
        self,
        path: str,
        endpoint: Callable[..., Any],
        method: str,
        *,
        status_code: Optional[int] = None,
        response_class: Any | None = None,
    ) -> None:
        self.path = path
        self.endpoint = endpoint
        self.method = method
        self.status_code = status_code
        self.response_class = response_class


class FastAPI:
    """필요한 기능만 구현한 경량 FastAPI."""

    def __init__(self, *, title: str = "", description: str = "", version: str = "") -> None:
        self.title = title
        self.description = description
        self.version = version
        self._routes: dict[tuple[str, str], Route] = {}
        self._middleware: list[tuple[type[Any], dict[str, Any]]] = []
        self._mounts: dict[str, Any] = {}

    # 미들웨어와 마운트는 테스트에서 사용되지 않으므로 정보를 보관만 한다.
    def add_middleware(self, middleware_cls: type[Any], **options: Any) -> None:
        self._middleware.append((middleware_cls, options))

    def mount(self, path: str, app: Any, name: str | None = None) -> None:
        self._mounts[path] = {"app": app, "name": name}

    def _register_route(
        self,
        path: str,
        endpoint: Callable[..., Any],
        methods: Iterable[str],
        *,
        status_code: Optional[int] = None,
        response_class: Any | None = None,
    ) -> Callable[..., Any]:
        for method in methods:
            key = (method.upper(), path)
            self._routes[key] = Route(
                path=path,
                endpoint=endpoint,
                method=method.upper(),
                status_code=status_code,
                response_class=response_class,
            )
        return endpoint

    def get(self, path: str, *, response_model: Any | None = None, response_class: Any | None = None) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        """GET 라우트 데코레이터."""

        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            return self._register_route(
                path,
                func,
                methods=("GET",),
                status_code=status.HTTP_200_OK,
                response_class=response_class,
            )

        return decorator

    def post(
        self,
        path: str,
        *,
        response_model: Any | None = None,
        response_class: Any | None = None,
        status_code: Optional[int] = None,
    ) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        """POST 라우트 데코레이터."""

        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            return self._register_route(
                path,
                func,
                methods=("POST",),
                status_code=status_code or status.HTTP_200_OK,
                response_class=response_class,
            )

        return decorator

    def _call_endpoint(self, route: Route, payload: Any) -> Any:
        endpoint = route.endpoint
        sig = inspect.signature(endpoint)
        kwargs: dict[str, Any] = {}
        for name, parameter in sig.parameters.items():
            if parameter.kind in (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD):
                continue
            if name == "request":
                kwargs[name] = Request(scope={})
            else:
                kwargs[name] = payload

        result = endpoint(**kwargs)
        if inspect.iscoroutine(result):
            return asyncio.run(result)
        return result

    def _handle_request(self, method: str, path: str, payload: Any = None) -> tuple[int, Any]:
        route = self._routes.get((method.upper(), path))
        if route is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Not Found")

        result = self._call_endpoint(route, payload)

        if hasattr(result, "status_code") and hasattr(result, "content"):
            return int(result.status_code), result

        return int(route.status_code or status.HTTP_200_OK), result


