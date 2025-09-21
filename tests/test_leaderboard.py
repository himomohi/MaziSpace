import asyncio

from app.game import Leaderboard


def test_submit_and_sort_leaderboard():
  board = Leaderboard(max_entries=3)
  asyncio.run(board.submit("Alice", 100))
  asyncio.run(board.submit("Bob", 150))
  asyncio.run(board.submit("Cara", 120))
  asyncio.run(board.submit("Dan", 90))

  entries = asyncio.run(board.entries())
  assert [entry.player_name for entry in entries] == ["Bob", "Cara", "Alice"]
  assert [entry.score for entry in entries] == [150, 120, 100]


def test_reject_negative_scores():
  board = Leaderboard()
  try:
    asyncio.run(board.submit("Test", -1))
  except ValueError:
    pass
  else:
    raise AssertionError("음수 점수는 허용되지 않아야 합니다.")


def test_name_normalization_and_trim():
  board = Leaderboard()
  asyncio.run(board.submit("   ", 50))
  asyncio.run(board.submit("VeryLongNameThatShouldBeTrimmedBeyondThirtyTwoCharacters", 60))

  entries = asyncio.run(board.entries())
  assert entries[0].player_name == "VeryLongNameThatShouldBeTrimmedBeyondThirtyTwoCharacters"[:32]
  assert entries[1].player_name == "무명 파일럿"
