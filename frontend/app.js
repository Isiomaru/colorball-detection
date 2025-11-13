// WebSocket接続
let ws = null;
let canvas, ctx;
let gameState = null;

// 初期化
document.addEventListener('DOMContentLoaded', () => {
    canvas = document.getElementById('gameCanvas');
    ctx = canvas.getContext('2d');
    
    connectWebSocket();
    setupEventListeners();
});

// WebSocket接続
function connectWebSocket() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    ws = new WebSocket(`${protocol}//${window.location.host}/ws`);
    
    ws.onopen = () => {
        console.log('WebSocket接続成功');
        updateConnectionStatus(true);
    };
    
    ws.onmessage = (event) => {
        gameState = JSON.parse(event.data);
        updateUI(gameState);
    };
    
    ws.onerror = (error) => {
        console.error('WebSocket エラー:', error);
        updateConnectionStatus(false);
    };
    
    ws.onclose = () => {
        console.log('WebSocket切断');
        updateConnectionStatus(false);
        // 5秒後に再接続
        setTimeout(connectWebSocket, 5000);
    };
}

// 接続状態更新
function updateConnectionStatus(connected) {
    const status = document.getElementById('status');
    if (connected) {
        status.innerHTML = '<span class="status-dot"></span><span>接続中</span>';
        status.style.background = 'rgba(0, 255, 136, 0.1)';
    } else {
        status.innerHTML = '<span>切断</span>';
        status.style.background = 'rgba(255, 0, 0, 0.1)';
    }
}

// イベントリスナー
function setupEventListeners() {
    document.getElementById('startBtn').addEventListener('click', () => {
        sendCommand('start_calculation');
    });
    
    document.getElementById('resetBtn').addEventListener('click', () => {
        sendCommand('reset');
    });
}

// コマンド送信
function sendCommand(command) {
    if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({ command }));
    }
}

// UI更新
function updateUI(state) {
    if (!state) return;
    
    // ボール位置更新
    updateBallPositions(state.ball_positions);
    
    // キャンバス描画
    drawCanvas(state);
    
    // ゲーム状態更新
    updateGameState(state.game_state);
    
    // グリッド更新
    updateGrid(state.map_data, state.hit_positions, state.revealed_scores);
    
    // 合計スコア更新
    updateTotalScore(state.total_score);
    
    // ヒット情報更新
    updateHitInfo(state.revealed_scores);
}

// ボール位置表示
function updateBallPositions(positions) {
    if (!positions) return;
    
    document.getElementById('pinkX').textContent = positions.pink.x;
    document.getElementById('pinkY').textContent = positions.pink.y;
    document.getElementById('cyanX').textContent = positions.cyan.x;
    document.getElementById('cyanY').textContent = positions.cyan.y;
}

// キャンバス描画
function drawCanvas(state) {
    // キャンバスクリア
    ctx.fillStyle = '#1a1a2e';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    
    // グリッド描画
    ctx.strokeStyle = 'rgba(102, 126, 234, 0.3)';
    ctx.lineWidth = 2;
    state.map_data.forEach((row, i) => {
        row.forEach((cell, j) => {
            const x = cell.x;
            const y = cell.y;
            
            // 枠
            ctx.strokeRect(x - 60, y - 60, 120, 120);
            
            // ラベル
            ctx.fillStyle = 'rgba(255, 255, 255, 0.5)';
            ctx.font = '12px Arial';
            ctx.fillText(`[${i},${j}]`, x - 20, y - 50);
        });
    });
    
    // ヒット位置ハイライト
    state.hit_positions.forEach(hit => {
        const cell = state.map_data[hit.row][hit.col];
        ctx.fillStyle = 'rgba(0, 255, 136, 0.2)';
        ctx.fillRect(cell.x - 60, cell.y - 60, 120, 120);
        ctx.strokeStyle = '#00ff88';
        ctx.lineWidth = 3;
        ctx.strokeRect(cell.x - 60, cell.y - 60, 120, 120);
    });
    
    // ボール描画
    if (state.ball_positions) {
        // Pink
        if (state.ball_positions.pink.radius > 0) {
            drawBall(
                state.ball_positions.pink.x,
                state.ball_positions.pink.y,
                state.ball_positions.pink.radius,
                '#ff6b9d'
            );
        }
        
        // Cyan
        if (state.ball_positions.cyan.radius > 0) {
            drawBall(
                state.ball_positions.cyan.x,
                state.ball_positions.cyan.y,
                state.ball_positions.cyan.radius,
                '#00d2ff'
            );
        }
    }
}

// ボール描画
function drawBall(x, y, r, color) {
    // 外周
    ctx.strokeStyle = color;
    ctx.lineWidth = 3;
    ctx.beginPath();
    ctx.arc(x, y, r, 0, Math.PI * 2);
    ctx.stroke();
    
    // 中心
    ctx.fillStyle = color;
    ctx.beginPath();
    ctx.arc(x, y, 3, 0, Math.PI * 2);
    ctx.fill();
    
    // グロー効果
    ctx.shadowBlur = 20;
    ctx.shadowColor = color;
    ctx.beginPath();
    ctx.arc(x, y, r, 0, Math.PI * 2);
    ctx.stroke();
    ctx.shadowBlur = 0;
}

// ゲーム状態表示
function updateGameState(state) {
    const stateEl = document.getElementById('gameState');
    const startBtn = document.getElementById('startBtn');
    
    switch(state) {
        case 'waiting':
            stateEl.innerHTML = '<h2>⏳ 待機中...</h2>';
            startBtn.disabled = false;
            break;
        case 'calculating':
            stateEl.innerHTML = '<h2>🔍 位置確認中...</h2>';
            startBtn.disabled = true;
            break;
        case 'showing':
            stateEl.innerHTML = '<h2>✨ スコア開示中...</h2>';
            startBtn.disabled = true;
            break;
        case 'result':
            stateEl.innerHTML = '<h2>🎉 結果表示</h2>';
            startBtn.disabled = true;
            break;
    }
}

// グリッド更新
function updateGrid(mapData, hitPositions, revealedScores) {
    const gridDisplay = document.getElementById('gridDisplay');
    gridDisplay.innerHTML = '';
    
    mapData.forEach((row, i) => {
        row.forEach((cell, j) => {
            const cellDiv = document.createElement('div');
            cellDiv.className = 'grid-cell';
            
            // ヒット判定
            const isHit = hitPositions.some(h => h.row === i && h.col === j);
            if (isHit) {
                cellDiv.classList.add('hit');
            }
            
            // 固定スコアは常に表示
            if (cell.fixed) {
                cellDiv.innerHTML = `
                    <div class="cell-label">[${i},${j}]</div>
                    <div class="cell-score fixed">${cell.score}</div>
                `;
            } else {
                // ランダムスコア: 開示判定
                const revealed = revealedScores.find(r => r.row === i && r.col === j);
                if (revealed) {
                    cellDiv.classList.add('revealed');
                    cellDiv.innerHTML = `
                        <div class="cell-label">[${i},${j}]</div>
                        <div class="cell-score">${cell.score}</div>
                    `;
                } else {
                    cellDiv.innerHTML = `
                        <div class="cell-label">[${i},${j}]</div>
                        <div class="cell-score mystery">?</div>
                    `;
                }
            }
            
            gridDisplay.appendChild(cellDiv);
        });
    });
}

// 合計スコア更新
function updateTotalScore(score) {
    const scoreEl = document.getElementById('totalScore');
    
    // カウントアップアニメーション
    const currentScore = parseInt(scoreEl.textContent) || 0;
    if (score !== currentScore) {
        animateScore(scoreEl, currentScore, score, 500);
    }
}

// スコアアニメーション
function animateScore(element, start, end, duration) {
    const startTime = performance.now();
    
    function update(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        
        // イージング（easeOutCubic）
        const easeProgress = 1 - Math.pow(1 - progress, 3);
        const current = Math.floor(start + (end - start) * easeProgress);
        
        element.textContent = current;
        
        if (progress < 1) {
            requestAnimationFrame(update);
        }
    }
    
    requestAnimationFrame(update);
}

// ヒット情報更新
function updateHitInfo(revealedScores) {
    const hitInfo = document.getElementById('hitInfo');
    
    if (revealedScores.length === 0) {
        hitInfo.innerHTML = '';
        return;
    }
    
    hitInfo.innerHTML = '<h4 style="margin-bottom: 15px;">🎯 獲得スコア</h4>';
    
    revealedScores.forEach((hit, index) => {
        setTimeout(() => {
            const hitDiv = document.createElement('div');
            hitDiv.className = 'hit-item';
            hitDiv.innerHTML = `
                <strong>[${hit.row},${hit.col}]</strong> 
                ${hit.color.toUpperCase()}: 
                <span style="color: #ffd700; font-weight: 700;">+${hit.score}</span>
            `;
            hitInfo.appendChild(hitDiv);
        }, index * 100);
    });
}

// キーボードショートカット
document.addEventListener('keydown', (e) => {
    if (e.key === 's' || e.key === 'S') {
        sendCommand('start_calculation');
    } else if (e.key === 'r' || e.key === 'R') {
        sendCommand('reset');
    }
});