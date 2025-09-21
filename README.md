# MaziSpace

FastAPI 기반의 싱글 플레이어 웹 게임 **MaziSpace** 입니다. 사용자는 우주선을 조작해 별을 수집하고 운석을 피하며 점수를 획득할 수 있으며, 서버와 연동된 리더보드에 점수를 기록할 수 있습니다.

## 주요 특징

- **FastAPI 백엔드**: 점수 제출과 리더보드 조회 API를 제공하며 CORS가 활성화되어 별도 클라이언트에서도 접근 가능합니다.
- **Jinja 템플릿 & 정적 자원**: 서버가 메인 페이지, 스타일, JavaScript 게임 로직을 제공합니다.
- **모던 UI**: CSS 글래스모피즘 스타일과 애니메이션을 적용해 미래지향적 분위기를 연출합니다.
- **리더보드 관리**: 동시성 안전한 `Leaderboard` 클래스로 상위 점수를 정렬/저장합니다.
- **테스트 커버리지**: 리더보드 로직과 FastAPI 엔드포인트에 대한 pytest 기반 테스트를 포함합니다.

## 빠른 시작

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt  # 또는 pyproject.toml 기반 설치
pip install -e ".[dev]"  # 테스트 및 개발 도구 설치
uvicorn app.main:app --reload
```

브라우저에서 [http://localhost:8000](http://localhost:8000)을 열면 게임을 플레이할 수 있습니다.

## API 요약

- `GET /api/leaderboard` : 현재 상위 점수 목록을 반환합니다.
- `POST /api/leaderboard` : `{ "player_name": str, "score": int }` payload로 점수를 제출합니다.

## 테스트

```bash
pytest
```

## 개발 노트

- 서버 메모리에서 리더보드를 관리하므로 실제 운영 시에는 영속 저장소 연동이 필요합니다.
- `Leaderboard` 클래스는 `max_entries` 값을 조정해 상위 N개의 점수만 유지할 수 있습니다.
