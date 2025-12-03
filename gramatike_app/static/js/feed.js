/**
 * Feed Page JavaScript
 * Handles feed interactions, comments, likes, notifications, amigues, and tic-tac-toe game
 */

// Global variables (set by template)
// window.currentUser - current username
// window.currentUserId - current user ID

// Helper function to escape HTML in JS
function escapeHtml(text) {
    if (!text) return '';
    const map = {'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#x27;'};
    return String(text).replace(/[&<>"']/g, c => map[c]);
}

// Like/Unlike post
async function likePost(postId) {
    try {
        const res = await fetch('/api/posts/' + postId + '/like', {method: 'POST'});
        const data = await res.json();
        // Reload to update
        location.reload();
    } catch(e) {
        console.error(e);
    }
}

// Toggle comments section
async function toggleComments(postId) {
    const div = document.getElementById('comments-' + postId);
    if(div.style.display === 'none') {
        div.style.display = 'block';
        try {
            const res = await fetch('/api/posts/' + postId + '/comentarios');
            const data = await res.json();
            const comentarios = data.comentarios || [];
            if(comentarios.length === 0) {
                div.innerHTML = '<p style="font-size:0.75rem;color:var(--text-dim);">Nenhum comentário.</p>';
            } else {
                div.innerHTML = comentarios.map(c => '<div style="background:#f9fafb;padding:0.5rem 0.7rem;border-radius:10px;margin-bottom:0.4rem;font-size:0.8rem;"><strong style="color:var(--primary);">@' + escapeHtml(c.usuario) + '</strong><p style="margin:0.2rem 0 0;">' + escapeHtml(c.conteudo) + '</p></div>').join('');
            }
        } catch(e) {
            div.innerHTML = '<p style="font-size:0.75rem;color:#c00;">Erro ao carregar comentários.</p>';
        }
    } else {
        div.style.display = 'none';
    }
}

// Search function
function executarBusca() {
    const termo = document.getElementById('search-input').value.trim();
    if(termo) {
        location.href = '/?q=' + encodeURIComponent(termo);
    }
}

// Toggle notifications panel
function toggleNotifications() {
    var panel = document.getElementById('notifications-panel');
    if (panel) {
        panel.style.display = panel.style.display === 'none' ? 'block' : 'none';
    }
}

// Load notifications
async function loadNotifications(containerId, badgeId) {
    const container = document.getElementById(containerId);
    const badge = document.getElementById(badgeId);
    if (!container) return;
    try {
        const res = await fetch('/api/notificacoes');
        const data = await res.json();
        const items = data.notificacoes || [];
        const unread = items.filter(n => !n.lida).length;
        if (badge) {
            if (unread > 0) {
                badge.textContent = unread > 9 ? '9+' : unread;
                badge.style.display = 'inline-block';
            } else {
                badge.style.display = 'none';
            }
        }
        if (items.length === 0) {
            container.innerHTML = '<div style="text-align:center;color:#999;font-size:0.75rem;padding:0.5rem;">Nenhuma notificação</div>';
        } else {
            container.innerHTML = items.slice(0, 10).map(n => {
                var cls = n.lida ? '' : 'background:#f0ebff;';
                return '<div style="padding:0.5rem;border-radius:10px;font-size:0.75rem;' + cls + 'cursor:pointer;" onclick="marcarNotificacao(' + n.id + ')">' +
                    '<strong style="color:var(--primary);">' + escapeHtml(n.tipo || 'Notificação') + '</strong>' +
                    '<p style="margin:0.2rem 0 0;color:var(--text-dim);">' + escapeHtml(n.mensagem || '') + '</p>' +
                    '</div>';
            }).join('');
        }
    } catch(e) {
        container.innerHTML = '<div style="text-align:center;color:#c00;font-size:0.75rem;padding:0.5rem;">Erro ao carregar</div>';
    }
}

// Mark notification as read
async function marcarNotificacao(id) {
    try {
        await fetch('/api/notificacoes/marcar-lida', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({notificacao_id: id})
        });
        loadNotifications('notifications-list', 'notifications-badge');
    } catch(e) {
        console.error(e);
    }
}

// Load amigues list
async function loadAmigues() {
    const container = document.getElementById('amigues-list');
    const empty = document.getElementById('amigues-empty');
    if (!container) return;
    try {
        const res = await fetch('/api/amigues');
        const data = await res.json();
        const amigues = data.amigues || [];
        if (amigues.length === 0) {
            container.innerHTML = '';
            if (empty) empty.style.display = 'block';
        } else {
            if (empty) empty.style.display = 'none';
            container.innerHTML = amigues.map(a => {
                var foto = a.foto_perfil || '/static/img/avatar-default.png';
                return '<a href="/u/' + encodeURIComponent(a.username) + '" style="display:flex;align-items:center;gap:0.5rem;text-decoration:none;padding:0.4rem;border-radius:12px;transition:background 0.2s;" onmouseover="this.style.background=\'#f5f0ff\'" onmouseout="this.style.background=\'transparent\'">' +
                    '<img src="' + escapeHtml(foto) + '" style="width:32px;height:32px;border-radius:50%;object-fit:cover;">' +
                    '<span style="font-size:0.8rem;font-weight:700;color:var(--primary);">@' + escapeHtml(a.username) + '</span>' +
                    '</a>';
            }).join('');
        }
    } catch(e) {
        container.innerHTML = '<div style="text-align:center;color:#c00;font-size:0.7rem;">Erro ao carregar amigues</div>';
    }
}

// Mobile toggle functions
function toggleMobileActionsCard() {
    var card = document.getElementById('mobile-actions-card');
    var icon = document.getElementById('triangle-svg');
    if (card && icon) {
        if (card.style.display === 'none') {
            card.style.display = 'block';
            icon.style.transform = 'rotate(180deg)';
        } else {
            card.style.display = 'none';
            icon.style.transform = 'rotate(0deg)';
        }
    }
}

function toggleMobileTicTacToe() {
    var game = document.getElementById('mobile-ttt-container');
    if (game) {
        game.style.display = game.style.display === 'none' ? 'block' : 'none';
    }
}

// Tic-Tac-Toe Game Logic
function initTicTacToe(boardId, statusId, resetId) {
    var boardEl = document.getElementById(boardId);
    var statusEl = document.getElementById(statusId);
    var resetEl = document.getElementById(resetId);
    if (!boardEl || !statusEl || !resetEl) return;
    
    var board = new Array(9).fill('');
    var HUMAN = 'X', AI = 'O';
    var gameOver = false;
    
    function setStatus(msg) { if(statusEl) statusEl.textContent = msg; }
    
    function render() {
        var cells = boardEl.querySelectorAll('button[data-i]');
        cells.forEach(function(btn) {
            var i = +btn.getAttribute('data-i');
            var v = board[i];
            btn.textContent = v || '';
            btn.disabled = !!v || gameOver;
        });
    }
    
    var wins = [[0,1,2],[3,4,5],[6,7,8],[0,3,6],[1,4,7],[2,5,8],[0,4,8],[2,4,6]];
    
    function winner(b) {
        for(var k=0; k<wins.length; k++) {
            var a=wins[k][0], c=wins[k][1], d=wins[k][2];
            if(b[a] && b[a]===b[c] && b[c]===b[d]) return b[a];
        }
        return null;
    }
    
    function empties(b) { var r=[]; for(var i=0;i<9;i++) { if(!b[i]) r.push(i);} return r; }
    function isDraw(b) { return empties(b).length===0 && !winner(b); }
    
    function tryWinMove(b, p) {
        var e = empties(b);
        for(var i=0; i<e.length; i++) {
            var idx = e[i];
            b[idx] = p;
            var w = winner(b);
            b[idx] = '';
            if(w===p) return idx;
        }
        return -1;
    }
    
    function aiPick() {
        var idx = tryWinMove(board, AI); if(idx!==-1) return idx;
        idx = tryWinMove(board, HUMAN); if(idx!==-1) return idx;
        if(!board[4]) return 4;
        var corners = [0,2,6,8];
        for(var i=0; i<corners.length; i++) { if(!board[corners[i]]) return corners[i]; }
        var sides = [1,3,5,7];
        for(var j=0; j<sides.length; j++) { if(!board[sides[j]]) return sides[j]; }
        return -1;
    }
    
    function endIfNeeded() {
        var w = winner(board);
        if(w) { gameOver=true; setStatus(w===HUMAN ? 'Você venceu!' : 'Robo venceu!'); render(); return true; }
        if(isDraw(board)) { gameOver=true; setStatus('Empate.'); render(); return true; }
        return false;
    }
    
    function humanMove(i) {
        if(gameOver || board[i]) return;
        board[i] = HUMAN;
        render();
        if(endIfNeeded()) return;
        setStatus('Robo pensando...');
        setTimeout(function() {
            var m = aiPick();
            if(m>=0) { board[m] = AI; }
            render();
            if(!endIfNeeded()) setStatus('Sua vez: você é X');
        }, 220);
    }
    
    boardEl.addEventListener('click', function(ev) {
        var t = ev.target;
        if(!(t && t.matches('button[data-i]'))) return;
        var i = +t.getAttribute('data-i');
        humanMove(i);
    });
    
    resetEl.addEventListener('click', function() {
        board = new Array(9).fill('');
        gameOver = false;
        setStatus('Sua vez: você é X');
        render();
    });
    
    setStatus('Sua vez: você é X');
    render();
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    loadAmigues();
    loadNotifications('notifications-list', 'notifications-badge');
    // Initialize both desktop and mobile tic-tac-toe games
    initTicTacToe('ttt_board', 'ttt_status', 'ttt_reset');
    initTicTacToe('mobile_ttt_board', 'mobile_ttt_status', 'mobile_ttt_reset');
});
