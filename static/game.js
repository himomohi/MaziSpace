const canvas = document.getElementById("gameCanvas");
const ctx = canvas.getContext("2d");

const scoreEl = document.getElementById("score");
const bestScoreEl = document.getElementById("bestScore");
const restartButton = document.getElementById("restartButton");
const leaderboardList = document.getElementById("leaderboard");
const leaderboardTemplate = document.getElementById("leaderboard-item");
const scoreForm = document.getElementById("scoreForm");
const playerNameInput = document.getElementById("playerName");
const gameOverDialog = document.getElementById("gameOverDialog");

const API_BASE = `${window.location.origin}/api`;

const state = {
  running: true,
  canSubmit: false,
  score: 0,
  bestScore: 0,
  lastTimestamp: 0,
  obstacleTimer: 0,
  starTimer: 0,
};

const ship = {
  width: 46,
  height: 58,
  x: canvas.width / 2 - 23,
  y: canvas.height - 80,
  speed: 260,
};

const input = {
  left: false,
  right: false,
};

const obstacles = [];
const stars = [];

function resetGame() {
  state.running = true;
  state.canSubmit = false;
  state.score = 0;
  state.obstacleTimer = 0;
  state.starTimer = 0;
  ship.x = canvas.width / 2 - ship.width / 2;
  obstacles.length = 0;
  stars.length = 0;
  scoreEl.textContent = state.score;
}

function spawnObstacle() {
  const width = 36 + Math.random() * 30;
  obstacles.push({
    x: Math.random() * (canvas.width - width),
    y: -width,
    width,
    height: width,
    speed: 120 + Math.random() * 80,
  });
}

function spawnStar() {
  const size = 16;
  stars.push({
    x: Math.random() * (canvas.width - size),
    y: -size,
    size,
    speed: 80 + Math.random() * 60,
  });
}

function updateShip(delta) {
  if (input.left) {
    ship.x -= ship.speed * delta;
  }
  if (input.right) {
    ship.x += ship.speed * delta;
  }
  ship.x = Math.max(0, Math.min(canvas.width - ship.width, ship.x));
}

function updateObstacles(delta) {
  state.obstacleTimer += delta;
  const interval = Math.max(0.6, 1.6 - state.score / 500);
  if (state.obstacleTimer > interval) {
    spawnObstacle();
    state.obstacleTimer = 0;
  }

  for (const obstacle of obstacles) {
    obstacle.y += obstacle.speed * delta;
  }

  for (let i = obstacles.length - 1; i >= 0; i -= 1) {
    const obstacle = obstacles[i];
    if (obstacle.y > canvas.height + 60) {
      obstacles.splice(i, 1);
      continue;
    }

    if (isColliding(
      ship.x,
      ship.y,
      ship.width,
      ship.height,
      obstacle.x,
      obstacle.y,
      obstacle.width,
      obstacle.height,
    )) {
      endGame();
      break;
    }
  }
}

function updateStars(delta) {
  state.starTimer += delta;
  const interval = Math.max(0.9, 2.2 - state.score / 400);
  if (state.starTimer > interval) {
    spawnStar();
    state.starTimer = 0;
  }

  for (const star of stars) {
    star.y += star.speed * delta;
  }

  for (let i = stars.length - 1; i >= 0; i -= 1) {
    const star = stars[i];
    if (star.y > canvas.height + star.size) {
      stars.splice(i, 1);
      continue;
    }

    if (
      isColliding(
        ship.x,
        ship.y,
        ship.width,
        ship.height,
        star.x,
        star.y,
        star.size,
        star.size,
      )
    ) {
      stars.splice(i, 1);
      incrementScore(25);
    }
  }
}

function incrementScore(amount) {
  state.score += amount;
  scoreEl.textContent = state.score;
  if (state.score > state.bestScore) {
    state.bestScore = state.score;
    bestScoreEl.textContent = state.bestScore;
  }
}

function drawBackground() {
  const gradient = ctx.createLinearGradient(0, 0, 0, canvas.height);
  gradient.addColorStop(0, "#0f1f3a");
  gradient.addColorStop(1, "#040910");
  ctx.fillStyle = gradient;
  ctx.fillRect(0, 0, canvas.width, canvas.height);

  ctx.fillStyle = "rgba(255, 255, 255, 0.1)";
  for (let i = 0; i < 80; i += 1) {
    const x = (i * 53 + state.score) % canvas.width;
    const y = (i * 97 + state.score * 0.4) % canvas.height;
    ctx.fillRect(x, y, 2, 2);
  }
}

function drawShip() {
  ctx.fillStyle = "#ff6f91";
  ctx.beginPath();
  ctx.moveTo(ship.x + ship.width / 2, ship.y);
  ctx.lineTo(ship.x + ship.width, ship.y + ship.height);
  ctx.lineTo(ship.x, ship.y + ship.height);
  ctx.closePath();
  ctx.fill();

  ctx.fillStyle = "#ffe8f0";
  ctx.fillRect(ship.x + ship.width / 2 - 6, ship.y + ship.height / 2, 12, 16);
}

function drawObstacles() {
  ctx.fillStyle = "#7289da";
  obstacles.forEach((obstacle) => {
    ctx.beginPath();
    ctx.arc(
      obstacle.x + obstacle.width / 2,
      obstacle.y + obstacle.height / 2,
      obstacle.width / 2,
      0,
      Math.PI * 2,
    );
    ctx.fill();
  });
}

function drawStars() {
  ctx.fillStyle = "#ffd166";
  stars.forEach((star) => {
    ctx.beginPath();
    ctx.moveTo(star.x + star.size / 2, star.y);
    for (let i = 1; i < 5; i += 1) {
      const angle = (i * Math.PI * 2) / 5;
      const radius = i % 2 === 0 ? star.size / 2 : star.size / 4;
      const sx = star.x + star.size / 2 + Math.sin(angle) * radius;
      const sy = star.y + star.size / 2 - Math.cos(angle) * radius;
      ctx.lineTo(sx, sy);
    }
    ctx.closePath();
    ctx.fill();
  });
}

function drawGame() {
  drawBackground();
  drawStars();
  drawObstacles();
  drawShip();
}

function isColliding(ax, ay, aw, ah, bx, by, bw, bh) {
  return ax < bx + bw && ax + aw > bx && ay < by + bh && ay + ah > by;
}

function endGame() {
  state.running = false;
  state.canSubmit = true;
  if (!gameOverDialog.open) {
    gameOverDialog.showModal();
  }
}

function gameLoop(timestamp) {
  let delta = 0;
  if (state.lastTimestamp) {
    delta = (timestamp - state.lastTimestamp) / 1000;
  }
  state.lastTimestamp = timestamp;

  if (state.running) {
    updateShip(delta);
    updateObstacles(delta);
    updateStars(delta);
  }

  drawGame();

  requestAnimationFrame(gameLoop);
}

function handleKeyDown(event) {
  if (event.key === "ArrowLeft") {
    input.left = true;
  } else if (event.key === "ArrowRight") {
    input.right = true;
  }
}

function handleKeyUp(event) {
  if (event.key === "ArrowLeft") {
    input.left = false;
  } else if (event.key === "ArrowRight") {
    input.right = false;
  }
}

async function fetchLeaderboard() {
  try {
    const response = await fetch(`${API_BASE}/leaderboard`);
    if (!response.ok) {
      throw new Error("리더보드를 불러오지 못했습니다.");
    }
    const data = await response.json();
    renderLeaderboard(data);
  } catch (error) {
    console.error(error);
  }
}

function renderLeaderboard(entries) {
  leaderboardList.innerHTML = "";
  entries.forEach((entry, index) => {
    const item = leaderboardTemplate.content.firstElementChild.cloneNode(true);
    item.querySelector(".rank").textContent = index + 1;
    item.querySelector(".name").textContent = entry.player_name;
    item.querySelector(".score").textContent = entry.score.toLocaleString();
    leaderboardList.appendChild(item);
  });

  if (!entries.length) {
    const empty = document.createElement("li");
    empty.textContent = "아직 기록이 없습니다.";
    leaderboardList.appendChild(empty);
  }
}

async function submitScore(name, score) {
  const payload = {
    player_name: name,
    score,
  };

  const response = await fetch(`${API_BASE}/leaderboard`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw new Error(body.detail || "점수 제출에 실패했습니다.");
  }

  const data = await response.json();
  renderLeaderboard(data);
  state.canSubmit = false;
}

scoreForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  if (!state.canSubmit) {
    alert("게임이 끝난 후에만 점수를 제출할 수 있습니다.");
    return;
  }

  const name = playerNameInput.value.trim();
  if (!name) {
    alert("이름을 입력하세요.");
    return;
  }

  try {
    await submitScore(name, state.score);
    alert("점수가 저장되었습니다!");
  } catch (error) {
    alert(error.message);
  }
});

restartButton.addEventListener("click", () => {
  resetGame();
  if (gameOverDialog.open) {
    gameOverDialog.close();
  }
});

window.addEventListener("keydown", handleKeyDown);
window.addEventListener("keyup", handleKeyUp);

gameOverDialog.addEventListener("close", () => {
  if (!state.running) {
    scoreForm.classList.add("highlight");
    setTimeout(() => scoreForm.classList.remove("highlight"), 1200);
  }
});

fetchLeaderboard();
resetGame();
requestAnimationFrame(gameLoop);
