/**
 * Game+ Quest League — API Service Layer
 * Wraps all backend FastAPI endpoints.
 */

const API_BASE = 'http://localhost:8000';

const api = {
  /** Generic JSON fetch helper */
  async _get(path) {
    const res = await fetch(`${API_BASE}${path}`);
    if (!res.ok) throw new Error(`API ${path} → ${res.status}`);
    return res.json();
  },

  async _post(path, body) {
    const res = await fetch(`${API_BASE}${path}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });
    if (!res.ok) throw new Error(`API ${path} → ${res.status}`);
    return res.json();
  },

  async _put(path, body) {
    const res = await fetch(`${API_BASE}${path}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });
    if (!res.ok) throw new Error(`API ${path} → ${res.status}`);
    return res.json();
  },

  async _patch(path) {
    const res = await fetch(`${API_BASE}${path}`, { method: 'PATCH' });
    if (!res.ok) throw new Error(`API ${path} → ${res.status}`);
    return res.json();
  },

  /* ── Users ──────────────────────────────── */
  getUsers(limit = 100)       { return this._get(`/users?limit=${limit}`); },
  getUserDetail(id)            { return this._get(`/users/${id}`); },

  /* ── User State ─────────────────────────── */
  getUserStates(limit = 100)   { return this._get(`/user_state?limit=${limit}`); },
  getUserState(id)             { return this._get(`/user_state/${id}`); },

  /* ── Leaderboard ────────────────────────── */
  getLeaderboard(limit = 10)   { return this._get(`/leaderboard?limit=${limit}`); },

  /* ── Quests ─────────────────────────────── */
  getQuests(activeOnly = false) { return this._get(`/quests?active_only=${activeOnly}`); },
  getQuest(id)                {  return this._get(`/quests/${id}`); },
  updateQuest(id, body)       {  return this._put(`/quests/${id}`, body); },
  toggleQuest(id)             {  return this._patch(`/quests/${id}/toggle`); },

  /* ── Awards ─────────────────────────────── */
  getAwards(limit = 100)       { return this._get(`/awards?limit=${limit}`); },
  getUserAwards(id, limit = 50){ return this._get(`/awards/user/${id}?limit=${limit}`); },

  /* ── Badge Awards ───────────────────────── */
  getBadgeAwards(limit = 100)  { return this._get(`/badge_awards?limit=${limit}`); },
  getUserBadges(id)            { return this._get(`/badge_awards/user/${id}`); },

  /* ── Notifications ──────────────────────── */
  getNotifications(limit = 100){ return this._get(`/notifications?limit=${limit}`); },
  getUserNotifications(id, lim = 50) { return this._get(`/notifications/user/${id}?limit=${lim}`); },

  /* ── What-If ────────────────────────────── */
  simulateWhatIf(userId, deltas) {
    return this._post('/whatif/simulate', { user_id: userId, deltas });
  },

  /* ── Pipeline ───────────────────────────── */
  runPipeline(asOfDate, sync = true) {
    let url = `/pipeline/run?sync=${sync}`;
    if (asOfDate) url += `&as_of_date=${asOfDate}`;
    return this._post(url, {});
  },

  /* ── DB Health ──────────────────────────── */
  getHealth() { return this._get('/health'); },
};
