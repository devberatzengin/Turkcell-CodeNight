/**
 * Game+ Quest League — Main Application
 * SPA router, rendering, and interaction logic.
 */

/* ── Quest Condition Formatter ────────────── */
function formatCondition(raw) {
  if (!raw) return '—';
  const conditionMap = {
    'login_count_today': { icon: '🔑', text: (v) => `Bugün en az ${v} kez giriş yapın` },
    'login_streak_days': { icon: '🔥', text: (v) => `${v} gün kesintisiz giriş serisi yakalayın` },
    'pvp_wins_today': { icon: '⚔️', text: (v) => `Bugün ${v} veya daha fazla PvP galibiyet kazanın` },
    'coop_minutes_today': { icon: '🤝', text: (v) => `Bugün ${v}+ dakika co-op oynayın` },
    'play_minutes_7d': { icon: '🎮', text: (v) => `Son 7 günde toplam ${v}+ dakika oynayın` },
    'topup_try_7d': { icon: '💰', text: (v) => `Son 7 günde ${v}+ TL harcama yapın` },
    'play_minutes_today': { icon: '🕹️', text: (v) => `Bugün ${v}+ dakika oynayın` },
    'topup_try_today': { icon: '💳', text: (v) => `Bugün ${v}+ TL harcama yapın` },
    'logins_7d': { icon: '📅', text: (v) => `Son 7 günde ${v}+ giriş yapın` },
  };

  // Try to match "metric >= value" pattern
  const match = raw.match(/^(\w+)\s*>=\s*(\d+)$/);
  if (match) {
    const [, metric, value] = match;
    const entry = conditionMap[metric];
    if (entry) return `${entry.icon} ${entry.text(value)}`;
  }

  // Special fallback for system quests
  if (raw.includes('same_user_same_day')) {
    return '⚙️ Aynı gün birden fazla görev tetiklenirse en yüksek öncelikli ödül seçilir';
  }

  // Generic fallback
  return raw.replace(/_/g, ' ').replace(/>=/, '≥');
}

/* ── Helpers ──────────────────────────────── */
const $ = (sel) => document.querySelector(sel);
const $$ = (sel) => [...document.querySelectorAll(sel)];

function formatDate(d) {
  if (!d) return '—';
  const dt = new Date(d);
  return dt.toLocaleDateString('tr-TR', { day: '2-digit', month: 'short', year: 'numeric' });
}
function formatDateTime(d) {
  if (!d) return '—';
  const dt = new Date(d);
  return dt.toLocaleDateString('tr-TR', { day: '2-digit', month: 'short', year: 'numeric' }) +
    ' ' + dt.toLocaleTimeString('tr-TR', { hour: '2-digit', minute: '2-digit' });
}
function initial(name) { return name ? name.charAt(0).toUpperCase() : '?'; }

function showToast(message, type = 'success') {
  const container = $('#toast-container');
  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  toast.textContent = message;
  container.appendChild(toast);
  setTimeout(() => toast.remove(), 3500);
}

/* ── Router ───────────────────────────────── */
const routes = {
    login: { title: 'Login', render: renderLogin },
  dashboard: { title: 'Dashboard', render: renderDashboard },
  leaderboard: { title: 'Leaderboard', render: renderLeaderboard },
  quests: { title: 'Quests', render: renderQuests },
  rewards: { title: 'Rewards', render: renderRewards },
  notifications: { title: 'Notifications', render: renderNotifications },
  whatif: { title: 'What-If', render: renderWhatIf },
  userDetail: { title: 'User Detail', render: renderUserDetail },
};

let currentRoute = 'login';
let currentUserId = null;

function navigate(route, params) {
    if (route !== 'login' && !currentUserId) {
        route = 'login';
    }
  currentRoute = route;
  if (params?.userId) currentUserId = params.userId;

  // Update active nav
  $$('.navbar-nav a').forEach(a => {
    a.classList.toggle('active', a.dataset.route === route);
  });

  // Hide all sections, show target
  $$('.section').forEach(s => s.classList.remove('active'));
  const target = $(`#section-${route}`);
  if (target) {
    target.classList.add('active');
    routes[route].render(params);
  }

  // Close mobile nav
  $('.navbar-nav')?.classList.remove('open');
}

/* ── Init ─────────────────────────────────── */
document.addEventListener('DOMContentLoaded', () => {
  // Nav links
  $$('.navbar-nav a[data-route]').forEach(a => {
    a.addEventListener('click', (e) => {
      e.preventDefault();
      navigate(a.dataset.route);
    });
  });

  // Profile dropdown
  const profileBtn = $('.navbar-profile');
  const dropdown = $('.profile-dropdown');
  if (profileBtn && dropdown) {
    profileBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      dropdown.classList.toggle('open');
    });
    document.addEventListener('click', () => dropdown.classList.remove('open'));
  }

  // Mobile toggle
  const toggle = $('.nav-toggle');
  if (toggle) {
    toggle.addEventListener('click', () => {
      $('.navbar-nav').classList.toggle('open');
    });
  }

  navigate('login');
});

/* ══════════════════════════════════════════════
   RENDER FUNCTIONS
   ══════════════════════════════════════════════ */

/* ── Login ─────────────────────────────────── */
async function renderLogin() {
    const container = $('#section-login');
    if (!container) return;

    container.innerHTML = `
      <div style="display:flex;justify-content:center;align-items:center;height:100vh;background:linear-gradient(135deg,#0f172a,#1e293b)">
        <div style="background:#1e293b;border:1px solid #334155;border-radius:12px;padding:40px;width:100%;max-width:380px;box-shadow:0 20px 60px rgba(0,0,0,0.5)">
          <h1 style="margin:0 0 8px;font-size:28px;font-weight:700;color:#eee">Game+</h1>
          <p style="margin:0 0 32px;color:#94a3b8;font-size:14px">Quest League</p>
          <form onsubmit="handleLogin(event)" style="display:flex;flex-direction:column;gap:16px">
            <div>
              <label style="display:block;margin-bottom:6px;color:#cbd5e1;font-size:13px;font-weight:500">Kullanıcı Adı veya ID</label>
              <input id="login-input" type="text" placeholder="Ece veya U5" required style="width:100%;padding:10px 12px;border:1px solid #475569;border-radius:6px;background:#0f172a;color:#e2e8f0;font-size:14px;box-sizing:border-box" />
            </div>
            <button type="submit" style="padding:10px;background:linear-gradient(90deg,#3b82f6,#8b5cf6);color:#fff;border:none;border-radius:6px;font-weight:600;cursor:pointer;font-size:14px;transition:0.2s">Giriş Yap</button>
          </form>
        </div>
      </div>
    `;
}

async function handleLogin(event) {
    if (event) event.preventDefault();
    const input = $('#login-input');
    if (!input) return;
    const value = input.value.trim();
    if (!value) {
        showToast('Lütfen kullanıcı adı girin', 'error');
        return;
    }

    try {
        const users = await api.getUsers();
        const lower = value.toLowerCase();
        const user = users.find(u =>
            (u.name && u.name.toLowerCase() === lower) ||
            (u.user_id && u.user_id.toLowerCase() === lower)
        );

        if (!user) {
            showToast('Kullanıcı bulunamadı', 'error');
            return;
        }

        currentUserId = user.user_id;
        const avatarEl = document.querySelector('.navbar-profile .avatar');
        if (avatarEl) avatarEl.textContent = (user.name|| user.user_id).charAt(0).toUpperCase();

        showToast(`Giriş yapıldı: ${user.name}`, 'success');
        navigate('dashboard');
    } catch (err) {
        showToast(`Hata: ${err.message}`, 'error');
    }
}

function handleLogout() {
    currentUserId = null;
    const avatarEl = document.querySelector('.navbar-profile .avatar');
    if (avatarEl) avatarEl.textContent = 'A';
    showToast('Oturumunuz kapatıldı', 'success');
    navigate('login');
}

/* ── Dashboard ────────────────────────────── */
async function renderDashboard() {
  const container = $('#section-dashboard');
  container.innerHTML = `<div class="loading"><div class="spinner"></div>Loading dashboard…</div>`;

  try {
    const [users, states, leaderboard] = await Promise.all([
      api.getUsers(),
      api.getUserStates(),
      api.getLeaderboard(100),
    ]);

    const awards = currentUserId
      ? await api.getUserAwards(currentUserId, 200)
      : await api.getAwards(100);

    // Merge user info with states
    const userMap = {};
    users.forEach(u => userMap[u.user_id] = u);
    states.forEach(s => s.name = userMap[s.user_id]?.name || s.user_id);

    // Logged-in user context
    const loggedInState = currentUserId ? states.find(s => s.user_id === currentUserId) : null;
    const loggedInLb = currentUserId ? leaderboard.find(l => l.user_id === currentUserId) : null;
    const loggedInUser = currentUserId ? userMap[currentUserId] : null;

    const effectiveState = loggedInState || {};
    const effectiveRank = loggedInLb?.rank ?? '—';
    const effectiveName = loggedInUser?.name || currentUserId || 'Oyuncu';

    // Stats summary
    const totalQuests = awards.length;
    const bestStreak = effectiveState.login_streak_days || 0;

    container.innerHTML = `
      <div class="welcome-banner" style="animation: slideUp 0.5s ease">
        <h2>Hoş geldin, <span class="welcome-name">${effectiveName}</span> 🎮</h2>
        <p>Görevlerini tamamla, puan kazan ve lider sıralamasına çık!</p>
      </div>

      <div class="stats-grid">
        <div class="stat-card" style="animation: slideUp 0.5s ease 0.1s both">
          <div class="stat-icon">🏆</div>
          <div class="stat-value">${effectiveState.total_points || 0}</div>
          <div class="stat-label">Senin Puanın</div>
          <div class="stat-bar" style="width: ${Math.min(100, (effectiveState.total_points || 0) / 15)}%"></div>
        </div>
        <div class="stat-card" style="animation: slideUp 0.5s ease 0.2s both">
          <div class="stat-icon">📊</div>
          <div class="stat-value">#${effectiveRank}</div>
          <div class="stat-label">Sıralaman</div>
          <div class="stat-bar" style="width: ${Math.min(100, ((6 - (effectiveRank || 5)) / 5) * 100)}%"></div>
        </div>
        <div class="stat-card" style="animation: slideUp 0.5s ease 0.3s both">
          <div class="stat-icon">⚔️</div>
          <div class="stat-value">${totalQuests}</div>
          <div class="stat-label">Görev Ödülü</div>
          <div class="stat-bar" style="width: ${Math.min(100, totalQuests * 10)}%"></div>
        </div>
        <div class="stat-card" style="animation: slideUp 0.5s ease 0.4s both">
          <div class="stat-icon">🔥</div>
          <div class="stat-value">${bestStreak}</div>
          <div class="stat-label">Giriş Serisi</div>
          <div class="stat-bar" style="width: ${Math.min(100, bestStreak * 15)}%"></div>
        </div>
      </div>

      <div class="section-header"><h1>All <span class="highlight">Players</span></h1><p>Click a player to view their details</p></div>
      <div class="users-grid" id="users-grid"></div>
    `;

    // Render user cards
    const grid = $('#users-grid');
    states.forEach((s, i) => {
      const u = userMap[s.user_id] || {};
      const rank = leaderboard.find(l => l.user_id === s.user_id)?.rank || '—';
      const card = document.createElement('div');
      card.className = 'user-card';
      card.style.animation = `slideUp 0.4s ease ${0.1 * i}s both`;
      card.innerHTML = `
        <div class="user-card-header">
          <div class="user-avatar">${initial(u.name)}</div>
          <div class="user-info">
            <h4>${u.name || s.user_id}</h4>
            <span class="user-segment">${u.segment || ''} · ${u.city || ''}</span>
          </div>
        </div>
        <div class="user-stats">
          <div class="user-stat"><span class="label">Points</span><span class="value">${s.total_points || 0}</span></div>
          <div class="user-stat"><span class="label">Rank</span><span class="value">#${rank}</span></div>
          <div class="user-stat"><span class="label">Streak</span><span class="value">${s.login_streak_days || 0}🔥</span></div>
          <div class="user-stat"><span class="label">Play 7d</span><span class="value">${s.play_minutes_7d || 0}m</span></div>
        </div>
      `;
      card.addEventListener('click', () => navigate('userDetail', { userId: s.user_id }));
      grid.appendChild(card);
    });
  } catch (err) {
    container.innerHTML = `<div class="empty-state"><div class="empty-icon">❌</div><p>Backend API çağrısı başarısız oldu.<br>Backend'in çalıştığından emin olun (http://localhost:8000).</p><p style="color:var(--text-muted);font-size:0.8rem;margin-top:8px">${err.message}</p></div>`;
  }
}

/* ── Leaderboard ──────────────────────────── */
async function renderLeaderboard() {
  const container = $('#section-leaderboard');
  container.innerHTML = `<div class="loading"><div class="spinner"></div>Loading leaderboard…</div>`;

  try {
    const [lb, users] = await Promise.all([
      api.getLeaderboard(100),
      api.getUsers(),
    ]);

    const nameMap = {};
    users.forEach(u => nameMap[u.user_id] = u.name);

    // Top 3 podium
    const top3 = lb.slice(0, 3);
    const classes = ['gold', 'silver', 'bronze'];
    const medals = ['🥇', '🥈', '🥉'];

    // Re-order for podium display: 2nd, 1st, 3rd
    const podiumOrder = top3.length >= 3 ? [top3[1], top3[0], top3[2]] : top3;
    const podiumClasses = top3.length >= 3 ? [classes[1], classes[0], classes[2]] : classes.slice(0, top3.length);

    let podiumHTML = '<div class="podium">';
    podiumOrder.forEach((entry, i) => {
      const cls = podiumClasses[i];
      const name = nameMap[entry.user_id] || entry.user_id;
      podiumHTML += `
        <div class="podium-item ${cls}" style="cursor:pointer" onclick="navigate('userDetail',{userId:'${entry.user_id}'})">
          <div class="podium-avatar">
            ${initial(name)}
            <span class="podium-rank">${entry.rank}</span>
          </div>
          <div class="podium-name">${name}</div>
          <div class="podium-points">${entry.total_points} pts</div>
          <div class="podium-base">${medals[classes.indexOf(cls)]}</div>
        </div>
      `;
    });
    podiumHTML += '</div>';

    // Full table
    let tableHTML = `
      <div class="card">
        <div class="card-header"><h3>Full Rankings</h3><span class="badge status-active">${lb.length} players</span></div>
        <table class="leaderboard-table">
          <thead><tr><th>Rank</th><th>Player</th><th>Total Points</th><th>Action</th></tr></thead>
          <tbody>
    `;

    lb.forEach(entry => {
      const name = nameMap[entry.user_id] || entry.user_id;
      const rankCls = entry.rank <= 3 ? `rank-${entry.rank}` : 'rank-other';
      tableHTML += `
        <tr>
          <td><span class="rank-badge ${rankCls}">${entry.rank}</span></td>
          <td style="display:flex;align-items:center;gap:12px">
            <div class="avatar" style="width:32px;height:32px;font-size:0.75rem">${initial(name)}</div>
            ${name}
          </td>
          <td style="font-weight:700;color:var(--yellow-500)">${entry.total_points}</td>
          <td><button class="btn btn-secondary btn-sm" onclick="navigate('userDetail',{userId:'${entry.user_id}'})">View</button></td>
        </tr>
      `;
    });

    tableHTML += '</tbody></table></div>';

    container.innerHTML = `
      <div class="section-header"><h1>🏆 <span class="highlight">Leaderboard</span></h1><p>Top players ranked by total points</p></div>
      ${podiumHTML}
      ${tableHTML}
    `;
  } catch (err) {
    container.innerHTML = `<div class="empty-state"><div class="empty-icon">❌</div><p>Leaderboard yüklenemedi</p><p style="color:var(--text-muted);font-size:0.8rem">${err.message}</p></div>`;
  }
}

/* ── Quests ───────────────────────────────── */
async function renderQuests() {
  const container = $('#section-quests');
  container.innerHTML = `<div class="loading"><div class="spinner"></div>Loading quests…</div>`;

  try {
    const quests = await api.getQuests(false);

    const typeLabelMap = { DAILY: 'daily', WEEKLY: 'weekly', STREAK: 'streak', SYSTEM: 'system' };

    let cardsHTML = '';
    quests.forEach((q, i) => {
      const typeCls = typeLabelMap[q.quest_type] || 'system';
      const isActive = q.is_active;
      cardsHTML += `
        <div class="quest-card" style="animation: slideUp 0.4s ease ${0.08 * i}s both">
          ${isActive ? '<div style="position:absolute;top:0;left:0;right:0;height:3px;background:linear-gradient(90deg,var(--blue-400),var(--yellow-500))"></div>' : ''}
          <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:8px">
            <span class="quest-type ${typeCls}">${q.quest_type || 'N/A'}</span>
            <button class="btn-toggle ${isActive ? 'on' : 'off'}" data-quest="${q.quest_id}" onclick="handleToggleQuest('${q.quest_id}')">
              ${isActive ? '● Active' : '○ Inactive'}
            </button>
          </div>
          <h4>${q.quest_name}</h4>
          <div class="quest-condition">📋 ${formatCondition(q.condition)}</div>
          <div class="quest-footer">
            <div class="quest-reward">⭐ ${q.reward_points || 0} pts</div>
            <span class="quest-priority">Priority: ${q.priority}</span>
          </div>
        </div>
      `;
    });

    container.innerHTML = `
      <div class="section-header">
        <h1>⚔️ <span class="highlight">Quests</span></h1>
        <p>Manage and view all game quests — toggle active status</p>
      </div>
      <div class="quests-grid">${cardsHTML}</div>
    `;
  } catch (err) {
    container.innerHTML = `<div class="empty-state"><div class="empty-icon">❌</div><p>Quests yüklenemedi</p><p style="color:var(--text-muted);font-size:0.8rem">${err.message}</p></div>`;
  }
}

async function handleToggleQuest(questId) {
  try {
    const res = await api.toggleQuest(questId);
    showToast(`${questId} → ${res.is_active ? 'Active' : 'Inactive'}`, 'success');
    renderQuests();
  } catch (err) {
    showToast(`Toggle failed: ${err.message}`, 'error');
  }
}

/* ── Rewards (Badges) ─────────────────────── */
async function renderRewards() {
  const container = $('#section-rewards');
  container.innerHTML = `<div class="loading"><div class="spinner"></div>Loading rewards…</div>`;

  try {
    const [badgeAwards, users] = await Promise.all([
      api.getBadgeAwards(),
      api.getUsers(),
    ]);

    const nameMap = {};
    users.forEach(u => nameMap[u.user_id] = u.name);

    const levelIconMap = { 1: 'bronze', 2: 'silver', 3: 'gold' };
    const levelEmoji = { 1: '🥉', 2: '🥈', 3: '🥇' };

    let cardsHTML = '';
    if (badgeAwards.length === 0) {
      cardsHTML = `<div class="empty-state" style="grid-column:1/-1"><div class="empty-icon">🏅</div><p>No badges awarded yet. Earn points to unlock badges!</p></div>`;
    } else {
      badgeAwards.forEach((ba, i) => {
        const lvlCls = levelIconMap[ba.level] || 'bronze';
        const emoji = levelEmoji[ba.level] || '🏅';
        cardsHTML += `
          <div class="badge-card" style="animation: slideUp 0.4s ease ${0.08 * i}s both">
            <div class="badge-icon ${lvlCls}">${emoji}</div>
            <h4>${ba.badge_name}</h4>
            <div class="badge-condition">${nameMap[ba.user_id] || ba.user_id}</div>
            <div style="margin-top:8px;font-size:0.75rem;color:var(--text-muted)">${formatDateTime(ba.awarded_at)}</div>
          </div>
        `;
      });
    }

    container.innerHTML = `
      <div class="section-header"><h1>🏅 <span class="highlight">Rewards & Badges</span></h1><p>All badge awards earned by players</p></div>
      <div class="badges-grid">${cardsHTML}</div>
    `;
  } catch (err) {
    container.innerHTML = `<div class="empty-state"><div class="empty-icon">❌</div><p>Rewards yüklenemedi</p><p style="color:var(--text-muted);font-size:0.8rem">${err.message}</p></div>`;
  }
}

/* ── Notifications ────────────────────────── */
async function renderNotifications() {
  const container = $('#section-notifications');
  container.innerHTML = `<div class="loading"><div class="spinner"></div>Loading notifications…</div>`;

  try {
    const [notifs, users] = await Promise.all([
      api.getNotifications(),
      api.getUsers(),
    ]);

    const nameMap = {};
    users.forEach(u => nameMap[u.user_id] = u.name);

    let rowsHTML = '';
    notifs.forEach(n => {
      rowsHTML += `
        <tr>
          <td><span class="channel-badge">📱 ${n.channel || 'BiP'}</span></td>
          <td style="font-weight:600">${nameMap[n.user_id] || n.user_id}</td>
          <td>${n.message || '—'}</td>
          <td style="color:var(--text-muted);font-size:0.8rem;white-space:nowrap">${formatDateTime(n.sent_at)}</td>
        </tr>
      `;
    });

    container.innerHTML = `
      <div class="section-header"><h1>🔔 <span class="highlight">Notifications</span></h1><p>All BiP notification records</p></div>
      <div class="card">
        <table class="notif-table">
          <thead><tr><th>Channel</th><th>Player</th><th>Message</th><th>Sent At</th></tr></thead>
          <tbody>${rowsHTML}</tbody>
        </table>
      </div>
    `;
  } catch (err) {
    container.innerHTML = `<div class="empty-state"><div class="empty-icon">❌</div><p>Notifications yüklenemedi</p><p style="color:var(--text-muted);font-size:0.8rem">${err.message}</p></div>`;
  }
}

/* ── What-If Simulator ────────────────────── */
async function renderWhatIf() {
  const container = $('#section-whatif');

  try {
    const users = await api.getUsers();

    let optionsHTML = users.map(u => `<option value="${u.user_id}">${u.name} (${u.user_id})</option>`).join('');

    container.innerHTML = `
      <div class="section-header"><h1>🔮 <span class="highlight">What-If Simulator</span></h1><p>Simulate metric changes and see which quest would trigger</p></div>
      <div class="whatif-form" id="whatif-form">
        <div class="form-group">
          <label>Player</label>
          <select id="whatif-user">${optionsHTML}</select>
        </div>
        <div class="form-group">
          <label>+ PvP Wins</label>
          <input type="number" id="whatif-pvp" value="0" min="0" />
        </div>
        <div class="form-group">
          <label>+ Login Count</label>
          <input type="number" id="whatif-login" value="0" min="0" />
        </div>
        <div class="form-group">
          <label>+ Play Minutes</label>
          <input type="number" id="whatif-play" value="0" min="0" />
        </div>
        <div class="form-group">
          <label>+ Coop Minutes</label>
          <input type="number" id="whatif-coop" value="0" min="0" />
        </div>
        <div class="form-group" style="display:flex;align-items:flex-end">
          <button class="btn btn-primary" onclick="runWhatIfSimulation()" style="width:100%">🔮 Simulate</button>
        </div>
      </div>
      <div id="whatif-result"></div>
    `;
  } catch (err) {
    container.innerHTML = `<div class="empty-state"><div class="empty-icon">❌</div><p>Simulator yüklenemedi</p></div>`;
  }
}

async function runWhatIfSimulation() {
  const userId = $('#whatif-user').value;
  const pvp = parseInt($('#whatif-pvp').value) || 0;
  const login = parseInt($('#whatif-login').value) || 0;
  const play = parseInt($('#whatif-play').value) || 0;
  const coop = parseInt($('#whatif-coop').value) || 0;

  const deltas = {};
  if (pvp > 0) deltas.pvp_wins_today = pvp;
  if (login > 0) deltas.login_count_today = login;
  if (play > 0) deltas.play_minutes_today = play;
  if (coop > 0) deltas.coop_minutes_today = coop;

  const resultDiv = $('#whatif-result');
  resultDiv.innerHTML = `<div class="loading"><div class="spinner"></div>Simulating…</div>`;

  try {
    const result = await api.simulateWhatIf(userId, deltas);

    const currentQuest = result.current?.selected_quest || 'None';
    const simQuest = result.simulated?.selected_quest || 'None';
    const currentPts = result.current?.reward_points || 0;
    const simPts = result.simulated?.reward_points || 0;

    const currentTriggered = result.current?.triggered_quests || [];
    const simTriggered = result.simulated?.triggered_quests || [];

    resultDiv.innerHTML = `
      <div class="whatif-result" style="animation: slideUp 0.4s ease">
        <h3 style="margin-bottom:16px;font-weight:700">Simulation Result for <span style="color:var(--yellow-500)">${userId}</span></h3>
        <div class="whatif-comparison">
          <div class="whatif-panel current">
            <h4 style="color:var(--danger);margin-bottom:12px">📌 Current</h4>
            <div style="margin-bottom:8px"><strong>Selected Quest:</strong> ${currentQuest}</div>
            <div style="margin-bottom:8px"><strong>Reward:</strong> <span style="color:var(--yellow-500)">${currentPts} pts</span></div>
            <div><strong>Triggered:</strong> ${Array.isArray(currentTriggered) ? currentTriggered.join(', ') : currentTriggered}</div>
          </div>
          <div class="whatif-arrow">→</div>
          <div class="whatif-panel simulated">
            <h4 style="color:var(--success);margin-bottom:12px">🔮 Simulated</h4>
            <div style="margin-bottom:8px"><strong>Selected Quest:</strong> ${simQuest}</div>
            <div style="margin-bottom:8px"><strong>Reward:</strong> <span style="color:var(--yellow-500)">${simPts} pts</span></div>
            <div><strong>Triggered:</strong> ${Array.isArray(simTriggered) ? simTriggered.join(', ') : simTriggered}</div>
          </div>
        </div>
        ${simQuest !== currentQuest ? `<div style="margin-top:16px;padding:12px;background:rgba(34,197,94,0.08);border-radius:8px;border:1px solid rgba(34,197,94,0.2);font-size:0.9rem">✅ Quest selection would change from <strong>${currentQuest}</strong> to <strong>${simQuest}</strong>!</div>` : `<div style="margin-top:16px;padding:12px;background:rgba(100,116,139,0.08);border-radius:8px;border:1px solid rgba(100,116,139,0.15);font-size:0.9rem">ℹ️ No change in quest selection.</div>`}
      </div>
    `;
  } catch (err) {
    resultDiv.innerHTML = `<div class="empty-state"><div class="empty-icon">⚠️</div><p>Simulation failed: ${err.message}</p></div>`;
  }
}

/* ── User Detail ──────────────────────────── */
async function renderUserDetail(params) {
  const userId = params?.userId || currentUserId;
  if (!userId) { navigate('dashboard'); return; }
  currentUserId = userId;

  const container = $('#section-userDetail');
  container.innerHTML = `<div class="loading"><div class="spinner"></div>Loading user detail…</div>`;

  try {
    const detail = await api.getUserDetail(userId);
    const user = detail.user;
    const state = detail.state || {};
    const awards = detail.recent_awards || [];
    const badges = detail.badges || [];
    const notifs = detail.notifications || [];

    // Hero
    let heroHTML = `
      <div class="detail-header">
        <button class="back-btn" onclick="navigate('dashboard')">← Back</button>
      </div>
      <div class="detail-hero" style="animation: slideUp 0.4s ease">
        <div class="hero-avatar">${initial(user.name)}</div>
        <div class="hero-info">
          <h2>${user.name} <span style="color:var(--yellow-500)">${user.user_id}</span></h2>
          <div class="hero-meta">
            <span>📍 ${user.city || '—'}</span>
            <span>🏷️ ${user.segment || '—'}</span>
            <span>🏆 ${state.total_points || 0} pts</span>
            <span>🔥 ${state.login_streak_days || 0} day streak</span>
          </div>
        </div>
      </div>
    `;

    // Today metrics
    let todayHTML = `
      <div class="card" style="margin-bottom:24px;animation:slideUp 0.4s ease 0.1s both">
        <div class="card-header"><h3>📅 Today Metrics</h3></div>
        <div class="metrics-grid">
          <div class="metric-item"><div class="metric-label">Login Count</div><div class="metric-value">${state.login_count_today || 0}</div></div>
          <div class="metric-item"><div class="metric-label">Play Minutes</div><div class="metric-value">${state.play_minutes_today || 0}</div></div>
          <div class="metric-item"><div class="metric-label">PvP Wins</div><div class="metric-value">${state.pvp_wins_today || 0}</div></div>
          <div class="metric-item"><div class="metric-label">Coop Minutes</div><div class="metric-value">${state.coop_minutes_today || 0}</div></div>
          <div class="metric-item"><div class="metric-label">TopUp TRY</div><div class="metric-value">${state.topup_try_today || 0}</div></div>
        </div>
      </div>
    `;

    // 7-day metrics
    let weekHTML = `
      <div class="card" style="margin-bottom:24px;animation:slideUp 0.4s ease 0.2s both">
        <div class="card-header"><h3>📈 Last 7 Days</h3></div>
        <div class="metrics-grid">
          <div class="metric-item"><div class="metric-label">Play Minutes (7d)</div><div class="metric-value">${state.play_minutes_7d || 0}</div></div>
          <div class="metric-item"><div class="metric-label">TopUp TRY (7d)</div><div class="metric-value">${state.topup_try_7d || 0}</div></div>
          <div class="metric-item"><div class="metric-label">Logins (7d)</div><div class="metric-value">${state.logins_7d || 0}</div></div>
          <div class="metric-item"><div class="metric-label">Login Streak</div><div class="metric-value highlight">${state.login_streak_days || 0} 🔥</div></div>
          <div class="metric-item"><div class="metric-label">Total Points</div><div class="metric-value highlight">${state.total_points || 0} ⭐</div></div>
        </div>
      </div>
    `;

    // Quest awards
    let awardsHTML = `
      <div class="card" style="margin-bottom:24px;animation:slideUp 0.4s ease 0.3s both">
        <div class="card-header"><h3>⚔️ Quest Awards</h3><span class="badge status-active">${awards.length} awards</span></div>
    `;

    if (awards.length === 0) {
      awardsHTML += `<div class="empty-state" style="padding:24px"><p>No quest awards yet</p></div>`;
    } else {
      // For each award, fetch triggered/suppressed from the awards endpoint
      let awardsDetailHTML = '';
      for (const aw of awards) {
        awardsDetailHTML += `
          <div style="padding:12px;border-radius:8px;background:rgba(255,255,255,0.02);margin-bottom:8px;border:1px solid var(--glass-border)">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px">
              <strong>${aw.award_id}</strong>
              <span style="font-size:0.8rem;color:var(--text-muted)">${formatDate(aw.as_of_date)}</span>
            </div>
            <div class="quest-detail-item selected">
              <span>✅ Selected: <strong>${aw.selected_quest}</strong></span>
              <span style="color:var(--yellow-500);font-weight:700">+${aw.reward_points} pts</span>
            </div>
          </div>
        `;
      }
      awardsHTML += awardsDetailHTML;
    }
    awardsHTML += '</div>';

    // Badges
    let badgesHTML = `
      <div class="card" style="margin-bottom:24px;animation:slideUp 0.4s ease 0.4s both">
        <div class="card-header"><h3>🏅 Earned Badges</h3></div>
    `;
    if (badges.length === 0) {
      badgesHTML += `<div class="empty-state" style="padding:24px"><p>No badges earned yet — keep going!</p></div>`;
    } else {
      badgesHTML += '<div class="badges-grid" style="gap:16px">';
      const levelIconMap = { 1: 'bronze', 2: 'silver', 3: 'gold' };
      const levelEmoji = { 1: '🥉', 2: '🥈', 3: '🥇' };
      badges.forEach(b => {
        const lvl = b.level || 1;
        badgesHTML += `
          <div class="badge-card" style="padding:24px">
            <div class="badge-icon ${levelIconMap[lvl] || 'bronze'}" style="width:56px;height:56px;font-size:1.5rem">${levelEmoji[lvl] || '🏅'}</div>
            <h4 style="font-size:0.95rem">${b.badge_name}</h4>
            <div class="badge-condition">${formatDateTime(b.awarded_at)}</div>
          </div>
        `;
      });
      badgesHTML += '</div>';
    }
    badgesHTML += '</div>';

    // Notifications
    let notifHTML = `
      <div class="card" style="animation:slideUp 0.4s ease 0.5s both">
        <div class="card-header"><h3>🔔 Notification Log</h3></div>
    `;
    if (notifs.length === 0) {
      notifHTML += `<div class="empty-state" style="padding:24px"><p>No notifications yet</p></div>`;
    } else {
      notifHTML += `<table class="notif-table"><thead><tr><th>Channel</th><th>Message</th><th>Sent</th></tr></thead><tbody>`;
      notifs.forEach(n => {
        notifHTML += `<tr>
          <td><span class="channel-badge">📱 ${n.channel || 'BiP'}</span></td>
          <td>${n.message || '—'}</td>
          <td style="color:var(--text-muted);font-size:0.8rem;white-space:nowrap">${formatDateTime(n.sent_at)}</td>
        </tr>`;
      });
      notifHTML += '</tbody></table>';
    }
    notifHTML += '</div>';

    container.innerHTML = heroHTML + todayHTML + weekHTML + awardsHTML + badgesHTML + notifHTML;

  } catch (err) {
    container.innerHTML = `<div class="empty-state"><div class="empty-icon">❌</div><p>User detail yüklenemedi</p><p style="color:var(--text-muted);font-size:0.8rem">${err.message}</p></div>`;
  }
}
