const canvas = document.getElementById('game');
const ctx = canvas.getContext('2d');
const scoreEl = document.getElementById('score');
const messageEl = document.getElementById('message');

const TILE = 20;
const COLS = 28;
const ROWS = 31;

// 0=empty, 1=wall, 2=dot, 3=power pellet, 4=ghost house
const MAP = [
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
    [1,2,2,2,2,2,2,2,2,2,2,2,2,1,1,2,2,2,2,2,2,2,2,2,2,2,2,1],
    [1,2,1,1,1,1,2,1,1,1,1,1,2,1,1,2,1,1,1,1,1,2,1,1,1,1,2,1],
    [1,3,1,1,1,1,2,1,1,1,1,1,2,1,1,2,1,1,1,1,1,2,1,1,1,1,3,1],
    [1,2,1,1,1,1,2,1,1,1,1,1,2,1,1,2,1,1,1,1,1,2,1,1,1,1,2,1],
    [1,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,1],
    [1,2,1,1,1,1,2,1,1,2,1,1,1,1,1,1,1,1,2,1,1,2,1,1,1,1,2,1],
    [1,2,1,1,1,1,2,1,1,2,1,1,1,1,1,1,1,1,2,1,1,2,1,1,1,1,2,1],
    [1,2,2,2,2,2,2,1,1,2,2,2,2,1,1,2,2,2,2,1,1,2,2,2,2,2,2,1],
    [1,1,1,1,1,1,2,1,1,1,1,1,0,1,1,0,1,1,1,1,1,2,1,1,1,1,1,1],
    [0,0,0,0,0,1,2,1,1,1,1,1,0,1,1,0,1,1,1,1,1,2,1,0,0,0,0,0],
    [0,0,0,0,0,1,2,1,1,0,0,0,0,0,0,0,0,0,0,1,1,2,1,0,0,0,0,0],
    [0,0,0,0,0,1,2,1,1,0,1,1,1,4,4,1,1,1,0,1,1,2,1,0,0,0,0,0],
    [1,1,1,1,1,1,2,1,1,0,1,4,4,4,4,4,4,1,0,1,1,2,1,1,1,1,1,1],
    [0,0,0,0,0,0,2,0,0,0,1,4,4,4,4,4,4,1,0,0,0,2,0,0,0,0,0,0],
    [1,1,1,1,1,1,2,1,1,0,1,4,4,4,4,4,4,1,0,1,1,2,1,1,1,1,1,1],
    [0,0,0,0,0,1,2,1,1,0,1,1,1,1,1,1,1,1,0,1,1,2,1,0,0,0,0,0],
    [0,0,0,0,0,1,2,1,1,0,0,0,0,0,0,0,0,0,0,1,1,2,1,0,0,0,0,0],
    [0,0,0,0,0,1,2,1,1,0,1,1,1,1,1,1,1,1,0,1,1,2,1,0,0,0,0,0],
    [1,1,1,1,1,1,2,1,1,0,1,1,1,1,1,1,1,1,0,1,1,2,1,1,1,1,1,1],
    [1,2,2,2,2,2,2,2,2,2,2,2,2,1,1,2,2,2,2,2,2,2,2,2,2,2,2,1],
    [1,2,1,1,1,1,2,1,1,1,1,1,2,1,1,2,1,1,1,1,1,2,1,1,1,1,2,1],
    [1,2,1,1,1,1,2,1,1,1,1,1,2,1,1,2,1,1,1,1,1,2,1,1,1,1,2,1],
    [1,3,2,2,1,1,2,2,2,2,2,2,2,0,0,2,2,2,2,2,2,2,1,1,2,2,3,1],
    [1,1,1,2,1,1,2,1,1,2,1,1,1,1,1,1,1,1,2,1,1,2,1,1,2,1,1,1],
    [1,1,1,2,1,1,2,1,1,2,1,1,1,1,1,1,1,1,2,1,1,2,1,1,2,1,1,1],
    [1,2,2,2,2,2,2,1,1,2,2,2,2,1,1,2,2,2,2,1,1,2,2,2,2,2,2,1],
    [1,2,1,1,1,1,1,1,1,1,1,1,2,1,1,2,1,1,1,1,1,1,1,1,1,1,2,1],
    [1,2,1,1,1,1,1,1,1,1,1,1,2,1,1,2,1,1,1,1,1,1,1,1,1,1,2,1],
    [1,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,1],
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
];

let map, score, lives, gameState, pacman, ghosts, frightTimer, dotCount;

const GHOST_COLORS = ['#ff0000', '#ffb8ff', '#00ffff', '#ffb852'];
const GHOST_NAMES = ['blinky', 'pinky', 'inky', 'clyde'];

function initGame() {
    map = MAP.map(row => [...row]);
    score = 0;
    lives = 3;
    dotCount = 0;
    map.forEach(row => row.forEach(cell => { if (cell === 2 || cell === 3) dotCount++; }));
    gameState = 'waiting';
    initPositions();
    messageEl.textContent = 'Press SPACE to start';
}

function initPositions() {
    pacman = {
        x: 14, y: 23, dir: 'left', nextDir: 'left',
        mouthAngle: 0.2, mouthDir: 1, animSpeed: 0.05
    };
    frightTimer = 0;
    ghosts = GHOST_COLORS.map((color, i) => ({
        x: 12 + i * 2, y: 14, color, name: GHOST_NAMES[i],
        dir: 'up', frightened: false, eaten: false,
        scatterTarget: [
            {x: COLS - 3, y: 0}, {x: 2, y: 0},
            {x: COLS - 1, y: ROWS - 1}, {x: 0, y: ROWS - 1}
        ][i],
        mode: 'scatter', releaseTimer: i * 120
    }));
}

function isWall(x, y) {
    if (x < 0 || x >= COLS || y < 0 || y >= ROWS) return false; // tunnel
    const cell = map[y][x];
    return cell === 1 || cell === 4;
}

function canMove(x, y, dir) {
    let nx = x, ny = y;
    if (dir === 'left') nx--;
    if (dir === 'right') nx++;
    if (dir === 'up') ny--;
    if (dir === 'down') ny++;
    // Tunnel wrap
    if (nx < 0) nx = COLS - 1;
    if (nx >= COLS) nx = 0;
    return !isWall(nx, ny);
}

function move(entity, dir) {
    if (dir === 'left') entity.x--;
    if (dir === 'right') entity.x++;
    if (dir === 'up') entity.y--;
    if (dir === 'down') entity.y++;
    // Tunnel wrap
    if (entity.x < 0) entity.x = COLS - 1;
    if (entity.x >= COLS) entity.x = 0;
}

function dist(x1, y1, x2, y2) {
    return Math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2);
}

function getGhostTarget(ghost) {
    if (ghost.eaten) return { x: 14, y: 14 }; // return to ghost house
    if (ghost.frightened) return { x: Math.floor(Math.random() * COLS), y: Math.floor(Math.random() * ROWS) };
    if (ghost.mode === 'scatter') return ghost.scatterTarget;

    // Chase mode targets
    switch (ghost.name) {
        case 'blinky': return { x: pacman.x, y: pacman.y };
        case 'pinky': {
            let tx = pacman.x, ty = pacman.y;
            if (pacman.dir === 'left') tx -= 4;
            if (pacman.dir === 'right') tx += 4;
            if (pacman.dir === 'up') { ty -= 4; tx -= 4; }
            if (pacman.dir === 'down') ty += 4;
            return { x: tx, y: ty };
        }
        case 'inky': {
            let ax = pacman.x, ay = pacman.y;
            if (pacman.dir === 'left') ax -= 2;
            if (pacman.dir === 'right') ax += 2;
            if (pacman.dir === 'up') ay -= 2;
            if (pacman.dir === 'down') ay += 2;
            const blinky = ghosts[0];
            return { x: 2 * ax - blinky.x, y: 2 * ay - blinky.y };
        }
        case 'clyde': {
            const d = dist(ghost.x, ghost.y, pacman.x, pacman.y);
            if (d > 8) return { x: pacman.x, y: pacman.y };
            return ghost.scatterTarget;
        }
    }
}

function oppositeDir(dir) {
    return { left: 'right', right: 'left', up: 'down', down: 'up' }[dir];
}

function moveGhost(ghost) {
    if (ghost.releaseTimer > 0) { ghost.releaseTimer--; return; }

    const target = getGhostTarget(ghost);
    const dirs = ['up', 'down', 'left', 'right'];
    let bestDir = ghost.dir;
    let bestDist = Infinity;

    for (const d of dirs) {
        if (d === oppositeDir(ghost.dir)) continue; // no reversing
        if (!canMove(ghost.x, ghost.y, d)) continue;
        let nx = ghost.x, ny = ghost.y;
        if (d === 'left') nx--; if (d === 'right') nx++;
        if (d === 'up') ny--; if (d === 'down') ny++;
        if (nx < 0) nx = COLS - 1; if (nx >= COLS) nx = 0;
        const dd = dist(nx, ny, target.x, target.y);
        if (dd < bestDist) { bestDist = dd; bestDir = d; }
    }

    ghost.dir = bestDir;
    if (canMove(ghost.x, ghost.y, ghost.dir)) {
        move(ghost, ghost.dir);
    }

    // Return to ghost house
    if (ghost.eaten && ghost.x === 14 && ghost.y === 14) {
        ghost.eaten = false;
        ghost.frightened = false;
    }
}

let frameCount = 0;
let modeTimer = 0;

function update() {
    if (gameState !== 'playing') return;
    frameCount++;

    // Mode switching
    modeTimer++;
    const inScatter = modeTimer < 420 || (modeTimer >= 1200 && modeTimer < 1620) ||
                      (modeTimer >= 2400 && modeTimer < 2520);
    ghosts.forEach(g => {
        if (!g.frightened && !g.eaten) {
            g.mode = inScatter ? 'scatter' : 'chase';
        }
    });

    // Move pacman every 3 frames
    if (frameCount % 3 === 0) {
        if (canMove(pacman.x, pacman.y, pacman.nextDir)) {
            pacman.dir = pacman.nextDir;
        }
        if (canMove(pacman.x, pacman.y, pacman.dir)) {
            move(pacman, pacman.dir);
        }

        // Eat dots
        const cell = map[pacman.y]?.[pacman.x];
        if (cell === 2) {
            map[pacman.y][pacman.x] = 0;
            score += 10;
            dotCount--;
        } else if (cell === 3) {
            map[pacman.y][pacman.x] = 0;
            score += 50;
            dotCount--;
            frightTimer = 360;
            ghosts.forEach(g => {
                if (!g.eaten) {
                    g.frightened = true;
                    g.dir = oppositeDir(g.dir);
                }
            });
        }

        // Check win
        if (dotCount <= 0) {
            gameState = 'won';
            messageEl.textContent = 'YOU WIN! Press SPACE to restart';
            return;
        }
    }

    // Move ghosts every 4 frames (slower than pacman)
    if (frameCount % 4 === 0) {
        ghosts.forEach(g => moveGhost(g));
    }

    // Frightened timer
    if (frightTimer > 0) {
        frightTimer--;
        if (frightTimer === 0) {
            ghosts.forEach(g => { g.frightened = false; });
        }
    }

    // Collision detection
    ghosts.forEach(g => {
        if (g.x === pacman.x && g.y === pacman.y) {
            if (g.frightened && !g.eaten) {
                g.eaten = true;
                score += 200;
            } else if (!g.eaten) {
                lives--;
                if (lives <= 0) {
                    gameState = 'gameover';
                    messageEl.textContent = 'GAME OVER! Press SPACE to restart';
                } else {
                    initPositions();
                }
            }
        }
    });

    // Mouth animation
    pacman.mouthAngle += pacman.animSpeed * pacman.mouthDir;
    if (pacman.mouthAngle >= 0.3) pacman.mouthDir = -1;
    if (pacman.mouthAngle <= 0.02) pacman.mouthDir = 1;

    scoreEl.textContent = `Score: ${score} | Lives: ${lives}`;
}

function draw() {
    ctx.fillStyle = '#000';
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    // Draw map
    for (let y = 0; y < ROWS; y++) {
        for (let x = 0; x < COLS; x++) {
            const cell = map[y][x];
            const px = x * TILE;
            const py = y * TILE;

            if (cell === 1) {
                ctx.fillStyle = '#2121de';
                ctx.fillRect(px, py, TILE, TILE);
                // Inner darker square for wall texture
                ctx.fillStyle = '#1919a6';
                ctx.fillRect(px + 2, py + 2, TILE - 4, TILE - 4);
            } else if (cell === 2) {
                ctx.fillStyle = '#ffb8ae';
                ctx.beginPath();
                ctx.arc(px + TILE / 2, py + TILE / 2, 2, 0, Math.PI * 2);
                ctx.fill();
            } else if (cell === 3) {
                ctx.fillStyle = '#ffb8ae';
                ctx.beginPath();
                ctx.arc(px + TILE / 2, py + TILE / 2, 6, 0, Math.PI * 2);
                ctx.fill();
            }
        }
    }

    // Draw pacman
    const px = pacman.x * TILE + TILE / 2;
    const py = pacman.y * TILE + TILE / 2;
    const angle = { right: 0, down: Math.PI / 2, left: Math.PI, up: -Math.PI / 2 }[pacman.dir];

    ctx.fillStyle = '#ffff00';
    ctx.beginPath();
    ctx.arc(px, py, TILE / 2 - 1, angle + pacman.mouthAngle * Math.PI,
            angle - pacman.mouthAngle * Math.PI + 2 * Math.PI);
    ctx.lineTo(px, py);
    ctx.fill();

    // Draw ghosts
    ghosts.forEach(g => {
        const gx = g.x * TILE;
        const gy = g.y * TILE;

        if (g.eaten) {
            // Just eyes
            drawGhostEyes(gx, gy, g.dir);
            return;
        }

        // Body
        if (g.frightened) {
            ctx.fillStyle = frightTimer < 120 && Math.floor(frightTimer / 10) % 2 === 0 ? '#fff' : '#2121de';
        } else {
            ctx.fillStyle = g.color;
        }

        // Ghost shape
        ctx.beginPath();
        ctx.arc(gx + TILE / 2, gy + TILE / 2 - 2, TILE / 2 - 1, Math.PI, 0);
        ctx.lineTo(gx + TILE - 1, gy + TILE - 1);
        // Wavy bottom
        const wave = Math.sin(frameCount * 0.2) > 0 ? 3 : -3;
        ctx.lineTo(gx + TILE * 0.75, gy + TILE - 1 + wave);
        ctx.lineTo(gx + TILE * 0.5, gy + TILE - 1);
        ctx.lineTo(gx + TILE * 0.25, gy + TILE - 1 + wave);
        ctx.lineTo(gx + 1, gy + TILE - 1);
        ctx.fill();

        if (!g.frightened) {
            drawGhostEyes(gx, gy, g.dir);
        } else {
            // Frightened face
            ctx.fillStyle = '#fff';
            ctx.fillRect(gx + 5, gy + 8, 3, 3);
            ctx.fillRect(gx + 12, gy + 8, 3, 3);
        }
    });
}

function drawGhostEyes(gx, gy, dir) {
    const eyeOffsetX = dir === 'left' ? -2 : dir === 'right' ? 2 : 0;
    const eyeOffsetY = dir === 'up' ? -2 : dir === 'down' ? 2 : 0;

    // White of eyes
    ctx.fillStyle = '#fff';
    ctx.beginPath();
    ctx.arc(gx + 7, gy + 8, 3, 0, Math.PI * 2);
    ctx.fill();
    ctx.beginPath();
    ctx.arc(gx + 13, gy + 8, 3, 0, Math.PI * 2);
    ctx.fill();

    // Pupils
    ctx.fillStyle = '#00f';
    ctx.beginPath();
    ctx.arc(gx + 7 + eyeOffsetX, gy + 8 + eyeOffsetY, 1.5, 0, Math.PI * 2);
    ctx.fill();
    ctx.beginPath();
    ctx.arc(gx + 13 + eyeOffsetX, gy + 8 + eyeOffsetY, 1.5, 0, Math.PI * 2);
    ctx.fill();
}

function gameLoop() {
    update();
    draw();
    requestAnimationFrame(gameLoop);
}

// Input
document.addEventListener('keydown', e => {
    const keyMap = {
        ArrowLeft: 'left', ArrowRight: 'right', ArrowUp: 'up', ArrowDown: 'down',
        a: 'left', d: 'right', w: 'up', s: 'down',
        A: 'left', D: 'right', W: 'up', S: 'down'
    };

    if (keyMap[e.key]) {
        e.preventDefault();
        pacman.nextDir = keyMap[e.key];
    }

    if (e.key === ' ') {
        e.preventDefault();
        if (gameState === 'waiting' || gameState === 'gameover' || gameState === 'won') {
            if (gameState === 'gameover' || gameState === 'won') {
                initGame();
            }
            gameState = 'playing';
            messageEl.textContent = '';
            frameCount = 0;
            modeTimer = 0;
        }
    }
});

initGame();
gameLoop();
