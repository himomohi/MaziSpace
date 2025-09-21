from fastapi.testclient import TestClient

from app.game import Leaderboard
from app.main import create_app


def create_client():
  board = Leaderboard()
  app = create_app(board)
  return TestClient(app), board


def test_get_empty_leaderboard():
  client, _ = create_client()
  response = client.get("/api/leaderboard")
  assert response.status_code == 200
  assert response.json() == []


def test_submit_score_and_fetch():
  client, _ = create_client()
  response = client.post("/api/leaderboard", json={"player_name": "Ace", "score": 320})
  assert response.status_code == 201
  data = response.json()
  assert data[0]["player_name"] == "Ace"
  assert data[0]["score"] == 320

  response = client.post("/api/leaderboard", json={"player_name": "Nova", "score": 420})
  assert response.status_code == 201
  data = response.json()
  assert [entry["player_name"] for entry in data] == ["Nova", "Ace"]

  response = client.get("/api/leaderboard")
  assert response.status_code == 200
  assert [entry["score"] for entry in response.json()] == [420, 320]


def test_submit_invalid_score():
  client, _ = create_client()
  response = client.post("/api/leaderboard", json={"player_name": "Bad", "score": -5})
  assert response.status_code == 400
  assert "점수" in response.json()["detail"]
