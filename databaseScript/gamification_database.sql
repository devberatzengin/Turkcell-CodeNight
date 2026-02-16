-- 1st SCRIPT


-- ============================================
-- Gamification System Database - PostgreSQL
-- Complete schema with relationships and data
-- ============================================

BEGIN;

-- Drop existing tables if they exist (in reverse order of dependencies)
DROP TABLE IF EXISTS notifications CASCADE;
DROP TABLE IF EXISTS leaderboard CASCADE;
DROP TABLE IF EXISTS quest_decisions CASCADE;
DROP TABLE IF EXISTS points_ledger CASCADE;
DROP TABLE IF EXISTS quest_awards CASCADE;
DROP TABLE IF EXISTS badge_awards CASCADE;
DROP TABLE IF EXISTS activity_events CASCADE;
DROP TABLE IF EXISTS user_state CASCADE;
DROP TABLE IF EXISTS quests CASCADE;
DROP TABLE IF EXISTS badges CASCADE;
DROP TABLE IF EXISTS games CASCADE;
DROP TABLE IF EXISTS users CASCADE;

-- ============================================
-- TABLE DEFINITIONS
-- ============================================

-- Users table (Main user data)
CREATE TABLE users (
    user_id VARCHAR(10) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    city VARCHAR(100),
    segment VARCHAR(50)
);

-- Games table
CREATE TABLE games (
    game_id VARCHAR(10) PRIMARY KEY,
    game_name VARCHAR(100) NOT NULL,
    genre VARCHAR(50)
);

-- Badges table
CREATE TABLE badges (
    badge_id VARCHAR(10) PRIMARY KEY,
    badge_name VARCHAR(100) NOT NULL,
    condition VARCHAR(255),
    level INTEGER
);

-- Quests table
CREATE TABLE quests (
    quest_id VARCHAR(10) PRIMARY KEY,
    quest_name VARCHAR(100) NOT NULL,
    quest_type VARCHAR(50),
    condition VARCHAR(255),
    reward_points INTEGER,
    priority INTEGER,
    is_active BOOLEAN
);

-- User state table (Current user metrics)
CREATE TABLE user_state (
    user_id VARCHAR(10) PRIMARY KEY,
    name VARCHAR(100),
    city VARCHAR(100),
    segment VARCHAR(50),
    login_count_today INTEGER DEFAULT 0,
    play_minutes_today INTEGER DEFAULT 0,
    pvp_wins_today INTEGER DEFAULT 0,
    coop_minutes_today INTEGER DEFAULT 0,
    topup_try_today INTEGER DEFAULT 0,
    play_minutes_7d INTEGER DEFAULT 0,
    topup_try_7d INTEGER DEFAULT 0,
    logins_7d INTEGER DEFAULT 0,
    login_streak_days INTEGER DEFAULT 0,
    total_points INTEGER DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- Activity events table
CREATE TABLE activity_events (
    event_id VARCHAR(50) PRIMARY KEY,
    user_id VARCHAR(10) NOT NULL,
    date DATE NOT NULL,
    game_id VARCHAR(10),
    login_count INTEGER DEFAULT 0,
    play_minutes INTEGER DEFAULT 0,
    pvp_wins INTEGER DEFAULT 0,
    coop_minutes INTEGER DEFAULT 0,
    topup_try INTEGER DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (game_id) REFERENCES games(game_id) ON DELETE SET NULL
);

-- Badge awards table
CREATE TABLE badge_awards (
    award_id SERIAL PRIMARY KEY,
    user_id VARCHAR(10) NOT NULL,
    badge_id VARCHAR(10) NOT NULL,
    awarded_at TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (badge_id) REFERENCES badges(badge_id) ON DELETE CASCADE
);

-- Quest awards table
CREATE TABLE quest_awards (
    award_id VARCHAR(50) PRIMARY KEY,
    user_id VARCHAR(10) NOT NULL,
    as_of_date DATE NOT NULL,
    triggered_quests TEXT,
    selected_quest VARCHAR(10),
    reward_points INTEGER,
    suppressed_quests TEXT,
    timestamp TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (selected_quest) REFERENCES quests(quest_id) ON DELETE SET NULL
);

-- Points ledger table
CREATE TABLE points_ledger (
    ledger_id VARCHAR(50) PRIMARY KEY,
    user_id VARCHAR(10) NOT NULL,
    points_delta INTEGER NOT NULL,
    source VARCHAR(50),
    source_ref VARCHAR(50),  -- references quest_awards.award_id
    created_at TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (source_ref) REFERENCES quest_awards(award_id) ON DELETE SET NULL
);

-- Quest decisions table
CREATE TABLE quest_decisions (
    decision_id VARCHAR(10) PRIMARY KEY,
    user_id VARCHAR(10) NOT NULL,
    as_of_date DATE NOT NULL,
    selected_reward_points INTEGER,
    reason TEXT,
    timestamp TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- Leaderboard table
CREATE TABLE leaderboard (
    rank INTEGER PRIMARY KEY,
    user_id VARCHAR(10) NOT NULL,
    total_points INTEGER,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- Notifications table
CREATE TABLE notifications (
    notification_id VARCHAR(50) PRIMARY KEY,
    user_id VARCHAR(10) NOT NULL,
    channel VARCHAR(50),
    message TEXT,
    sent_at TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- ============================================
-- DATA INSERTION
-- ============================================

-- Insert Users
INSERT INTO users (user_id, name, city, segment) VALUES
('U1', 'Ayşe', 'Istanbul', 'STUDENT'),
('U2', 'Ali', 'Ankara', 'STUDENT'),
('U3', 'Deniz', 'Izmir', 'STUDENT'),
('U4', 'Mert', 'Bursa', 'YOUNG_PRO'),
('U5', 'Ece', 'Antalya', 'YOUNG_PRO');

-- Insert Games
INSERT INTO games (game_id, game_name, genre) VALUES
('G1', 'Arena Rivals', 'PVP'),
('G2', 'Sky Builders', 'CASUAL'),
('G3', 'Cyber Run', 'RUNNER'),
('G4', 'Mystic Raid', 'COOP');

-- Insert Badges
INSERT INTO badges (badge_id, badge_name, condition, level) VALUES
('B-01', 'Bronz Oyuncu', 'total_points >= 300', 1),
('B-02', 'Gümüş Oyuncu', 'total_points >= 800', 2),
('B-03', 'Altın Oyuncu', 'total_points >= 1500', 3);

-- Insert Quests
INSERT INTO quests (quest_id, quest_name, quest_type, condition, reward_points, priority, is_active) VALUES
('Q-01', 'Günlük Giriş', 'DAILY', 'login_count_today >= 1', 50, 5, TRUE),
('Q-02', 'Kesintisiz Seri', 'STREAK', 'login_streak_days >= 3', 150, 4, TRUE),
('Q-03', 'PvP Ustası', 'DAILY', 'pvp_wins_today >= 3', 200, 2, TRUE),
('Q-04', 'Coop Takım Oyunu', 'DAILY', 'coop_minutes_today >= 60', 180, 3, TRUE),
('Q-05', 'Haftalık Maraton', 'WEEKLY', 'play_minutes_7d >= 600', 500, 6, TRUE),
('Q-06', 'Harcamaya Ödül', 'WEEKLY', 'topup_try_7d >= 200', 250, 7, TRUE),
('Q-07', 'Çakışma Kuralı (Tek Ödül)', 'SYSTEM', 'same_user_same_day_only_highest_priority_reward', 0, 1, TRUE);

-- Insert User State
INSERT INTO user_state (user_id, name, city, segment, login_count_today, play_minutes_today, pvp_wins_today, coop_minutes_today, topup_try_today, play_minutes_7d, topup_try_7d, logins_7d, login_streak_days, total_points) VALUES
('U1', 'Ayşe', 'Istanbul', 'STUDENT', 1, 137, 0, 30, 0, 516, 150, 5, 5, 150),
('U2', 'Ali', 'Ankara', 'STUDENT', 1, 64, 1, 13, 0, 376, 250, 5, 5, 150),
('U3', 'Deniz', 'Izmir', 'STUDENT', 1, 82, 1, 87, 100, 342, 500, 5, 5, 180),
('U4', 'Mert', 'Bursa', 'YOUNG_PRO', 1, 144, 1, 19, 0, 632, 200, 5, 5, 150),
('U5', 'Ece', 'Antalya', 'YOUNG_PRO', 1, 157, 4, 14, 0, 552, 100, 5, 5, 200);

-- Insert Activity Events
INSERT INTO activity_events (event_id, user_id, date, game_id, login_count, play_minutes, pvp_wins, coop_minutes, topup_try) VALUES
('E-1', 'U1', '2026-03-08', 'G3', 1, 68, 1, 20, 0),
('E-2', 'U1', '2026-03-09', 'G1', 1, 48, 4, 3, 0),
('E-3', 'U1', '2026-03-10', 'G4', 1, 179, 0, 116, 100),
('E-4', 'U1', '2026-03-11', 'G1', 1, 84, 0, 2, 50),
('E-5', 'U1', '2026-03-12', 'G4', 1, 137, 0, 30, 0),
('E-6', 'U2', '2026-03-08', 'G1', 1, 138, 0, 18, 0),
('E-7', 'U2', '2026-03-09', 'G2', 1, 87, 2, 20, 100),
('E-8', 'U2', '2026-03-10', 'G4', 1, 45, 2, 74, 50),
('E-9', 'U2', '2026-03-11', 'G4', 1, 42, 0, 5, 100),
('E-10', 'U2', '2026-03-12', 'G3', 1, 64, 1, 13, 0),
('E-11', 'U3', '2026-03-08', 'G4', 1, 60, 2, 39, 100),
('E-12', 'U3', '2026-03-09', 'G4', 1, 76, 0, 74, 100),
('E-13', 'U3', '2026-03-10', 'G1', 1, 78, 2, 3, 100),
('E-14', 'U3', '2026-03-11', 'G1', 1, 46, 4, 1, 100),
('E-15', 'U3', '2026-03-12', 'G4', 1, 82, 1, 87, 100),
('E-16', 'U4', '2026-03-08', 'G2', 1, 110, 1, 18, 50),
('E-17', 'U4', '2026-03-09', 'G4', 1, 122, 1, 31, 0),
('E-18', 'U4', '2026-03-10', 'G2', 1, 92, 0, 18, 0),
('E-19', 'U4', '2026-03-11', 'G2', 1, 164, 1, 10, 150),
('E-20', 'U4', '2026-03-12', 'G2', 1, 144, 1, 19, 0),
('E-21', 'U5', '2026-03-08', 'G3', 1, 161, 1, 5, 0),
('E-22', 'U5', '2026-03-09', 'G4', 1, 68, 1, 53, 0),
('E-23', 'U5', '2026-03-10', 'G1', 1, 49, 4, 18, 0),
('E-24', 'U5', '2026-03-11', 'G3', 1, 117, 2, 11, 100),
('E-25', 'U5', '2026-03-12', 'G1', 1, 157, 4, 14, 0);

-- Insert Quest Awards
INSERT INTO quest_awards (award_id, user_id, as_of_date, triggered_quests, selected_quest, reward_points, suppressed_quests, timestamp) VALUES
('QA-100', 'U1', '2026-03-12', 'Q-02|Q-01', 'Q-02', 150, 'Q-01', '2026-03-12 21:00:00'),
('QA-101', 'U2', '2026-03-12', 'Q-02|Q-01|Q-06', 'Q-02', 150, 'Q-01|Q-06', '2026-03-12 20:56:00'),
('QA-102', 'U3', '2026-03-12', 'Q-04|Q-02|Q-01|Q-06', 'Q-04', 180, 'Q-02|Q-01|Q-06', '2026-03-12 20:52:00'),
('QA-103', 'U4', '2026-03-12', 'Q-02|Q-01|Q-05|Q-06', 'Q-02', 150, 'Q-01|Q-05|Q-06', '2026-03-12 20:48:00'),
('QA-104', 'U5', '2026-03-12', 'Q-03|Q-02|Q-01', 'Q-03', 200, 'Q-02|Q-01', '2026-03-12 20:44:00');

-- Insert Points Ledger
INSERT INTO points_ledger (ledger_id, user_id, points_delta, source, source_ref, created_at) VALUES
('L-300', 'U1', 150, 'QUEST_REWARD', 'QA-100', '2026-03-12 21:00:00'),
('L-301', 'U2', 150, 'QUEST_REWARD', 'QA-101', '2026-03-12 20:56:00'),
('L-302', 'U3', 180, 'QUEST_REWARD', 'QA-102', '2026-03-12 20:52:00'),
('L-303', 'U4', 150, 'QUEST_REWARD', 'QA-103', '2026-03-12 20:48:00'),
('L-304', 'U5', 200, 'QUEST_REWARD', 'QA-104', '2026-03-12 20:44:00');

-- Insert Quest Decisions
INSERT INTO quest_decisions (decision_id, user_id, as_of_date, selected_reward_points, reason, timestamp) VALUES
('DQ-200', 'U1', '2026-03-12', 150, 'selected_quest=Q-02; priority=min', '2026-03-12 21:00:00'),
('DQ-201', 'U2', '2026-03-12', 150, 'selected_quest=Q-02; priority=min', '2026-03-12 20:56:00'),
('DQ-202', 'U3', '2026-03-12', 180, 'selected_quest=Q-04; priority=min', '2026-03-12 20:52:00'),
('DQ-203', 'U4', '2026-03-12', 150, 'selected_quest=Q-02; priority=min', '2026-03-12 20:48:00'),
('DQ-204', 'U5', '2026-03-12', 200, 'selected_quest=Q-03; priority=min', '2026-03-12 20:44:00');

-- Insert Leaderboard
INSERT INTO leaderboard (rank, user_id, total_points) VALUES
(1, 'U5', 200),
(2, 'U3', 180),
(3, 'U1', 150),
(4, 'U2', 150),
(5, 'U4', 150);

-- Insert Notifications
INSERT INTO notifications (notification_id, user_id, channel, message, sent_at) VALUES
('N-400', 'U1', 'BiP', 'Kazanım: Q-02 görevi tamamlandı. +150 puan.', '2026-03-12 21:00:00'),
('N-401', 'U2', 'BiP', 'Kazanım: Q-02 görevi tamamlandı. +150 puan.', '2026-03-12 20:56:00'),
('N-402', 'U3', 'BiP', 'Kazanım: Q-04 görevi tamamlandı. +180 puan.', '2026-03-12 20:52:00'),
('N-403', 'U4', 'BiP', 'Kazanım: Q-02 görevi tamamlandı. +150 puan.', '2026-03-12 20:48:00'),
('N-404', 'U5', 'BiP', 'Kazanım: Q-03 görevi tamamlandı. +200 puan.', '2026-03-12 20:44:00');

-- Create indexes for better query performance
CREATE INDEX idx_activity_events_user_id ON activity_events(user_id);
CREATE INDEX idx_activity_events_date ON activity_events(date);
CREATE INDEX idx_activity_events_game_id ON activity_events(game_id);
CREATE INDEX idx_quest_awards_user_id ON quest_awards(user_id);
CREATE INDEX idx_points_ledger_user_id ON points_ledger(user_id);
CREATE INDEX idx_notifications_user_id ON notifications(user_id);
CREATE INDEX idx_leaderboard_rank ON leaderboard(rank);

COMMIT;

-- ============================================
-- Database setup completed successfully!
-- You can now run queries against the tables.
-- ============================================



-- 2nd SCRIPT



BEGIN;

-- ============================================
-- 1️⃣ DERIVED & REDUNDANT STRUCTURE TEMİZLEME
-- ============================================

-- Leaderboard artık derived olacak → tabloyu kaldır
DROP TABLE IF EXISTS leaderboard CASCADE;

-- Quest decisions gereksiz (quest_awards zaten decision içeriyor)
DROP TABLE IF EXISTS quest_decisions CASCADE;

-- user_state içindeki total_points derived → kaldır
ALTER TABLE user_state
DROP COLUMN IF EXISTS total_points;

-- user_state içinde name/city/segment duplicate → kaldır (users zaten tutuyor)
ALTER TABLE user_state
DROP COLUMN IF EXISTS name,
DROP COLUMN IF EXISTS city,
DROP COLUMN IF EXISTS segment;

-- ============================================
-- 2️⃣ QUEST_AWARDS NORMALİZASYONU
-- ============================================

-- triggered_quests ve suppressed_quests TEXT alanları normalize edilecek
ALTER TABLE quest_awards
DROP COLUMN IF EXISTS triggered_quests,
DROP COLUMN IF EXISTS suppressed_quests;

-- Quest award relation tablosu oluştur
CREATE TABLE IF NOT EXISTS quest_award_quests (
    award_id VARCHAR(50) NOT NULL REFERENCES quest_awards(award_id) ON DELETE CASCADE,
    quest_id VARCHAR(10) NOT NULL REFERENCES quests(quest_id) ON DELETE CASCADE,
    status VARCHAR(20) NOT NULL CHECK (status IN ('TRIGGERED','SUPPRESSED')),
    PRIMARY KEY (award_id, quest_id)
);

-- ============================================
-- 3️⃣ POINTS_LEDGER İYİLEŞTİRME
-- ============================================

-- source alanını constraint ile güvenli hale getirelim
ALTER TABLE points_ledger
ADD CONSTRAINT ck_points_ledger_source
CHECK (source IN ('QUEST_REWARD','BADGE_REWARD','ADMIN'));

-- ============================================
-- 4️⃣ LEADERBOARD DERIVED VIEW
-- ============================================

CREATE OR REPLACE VIEW leaderboard_view AS
SELECT
    u.user_id,
    COALESCE(SUM(pl.points_delta),0) AS total_points,
    RANK() OVER (
        ORDER BY COALESCE(SUM(pl.points_delta),0) DESC, u.user_id ASC
    ) AS rank
FROM users u
LEFT JOIN points_ledger pl ON u.user_id = pl.user_id
GROUP BY u.user_id;

-- ============================================
-- 5️⃣ BADGE THRESHOLD İYİLEŞTİRME (optional ama önerilir)
-- ============================================

-- Eğer badges.condition string yerine threshold kullanmak istersen:
-- ALTER TABLE badges ADD COLUMN threshold_points INTEGER;
-- UPDATE badges SET threshold_points = 300 WHERE badge_id = 'B-01';
-- UPDATE badges SET threshold_points = 800 WHERE badge_id = 'B-02';
-- UPDATE badges SET threshold_points = 1500 WHERE badge_id = 'B-03';

COMMIT;



-- 3rd SCRIPT



BEGIN;

-- =====================================================
-- 1️⃣ BADGE DUPLICATE ENGELLEME
-- =====================================================

ALTER TABLE badge_awards
DROP CONSTRAINT IF EXISTS uq_user_badge;

ALTER TABLE badge_awards
ADD CONSTRAINT uq_user_badge UNIQUE (user_id, badge_id);


-- =====================================================
-- 2️⃣ LEDGER IMMUTABLE (UPDATE / DELETE YASAK)
-- =====================================================

CREATE OR REPLACE FUNCTION fn_prevent_ledger_modification()
RETURNS TRIGGER AS $$
BEGIN
    RAISE EXCEPTION 'Points ledger is immutable. Update/Delete not allowed.';
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_no_update_points_ledger ON points_ledger;
CREATE TRIGGER trg_no_update_points_ledger
BEFORE UPDATE ON points_ledger
FOR EACH ROW
EXECUTE FUNCTION fn_prevent_ledger_modification();

DROP TRIGGER IF EXISTS trg_no_delete_points_ledger ON points_ledger;
CREATE TRIGGER trg_no_delete_points_ledger
BEFORE DELETE ON points_ledger
FOR EACH ROW
EXECUTE FUNCTION fn_prevent_ledger_modification();


-- =====================================================
-- 3️⃣ QUEST → LEDGER OTOMATİK INSERT
-- =====================================================

CREATE OR REPLACE FUNCTION fn_insert_ledger_from_quest_award()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO points_ledger (
        ledger_id,
        user_id,
        points_delta,
        source,
        source_ref,
        created_at
    )
    VALUES (
        CONCAT('L-', NEW.award_id),
        NEW.user_id,
        NEW.reward_points,
        'QUEST_REWARD',
        NEW.award_id,
        COALESCE(NEW.timestamp, NOW())
    );

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_quest_award_to_ledger ON quest_awards;
CREATE TRIGGER trg_quest_award_to_ledger
AFTER INSERT ON quest_awards
FOR EACH ROW
EXECUTE FUNCTION fn_insert_ledger_from_quest_award();


-- =====================================================
-- 4️⃣ BADGE THRESHOLD KOLONU
-- =====================================================

ALTER TABLE badges
ADD COLUMN IF NOT EXISTS threshold_points INTEGER;

UPDATE badges SET threshold_points = 300 WHERE badge_id = 'B-01';
UPDATE badges SET threshold_points = 800 WHERE badge_id = 'B-02';
UPDATE badges SET threshold_points = 1500 WHERE badge_id = 'B-03';


-- =====================================================
-- 5️⃣ LEDGER → BADGE OTOMATİK KONTROL
-- =====================================================

CREATE OR REPLACE FUNCTION fn_check_badge_after_ledger()
RETURNS TRIGGER AS $$
DECLARE
    v_total_points INTEGER;
    v_badge RECORD;
BEGIN
    -- Güncel toplam puanı ledger'dan hesapla
    SELECT COALESCE(SUM(points_delta),0)
    INTO v_total_points
    FROM points_ledger
    WHERE user_id = NEW.user_id;

    -- Threshold'a göre badge kontrolü
    FOR v_badge IN
        SELECT badge_id, threshold_points
        FROM badges
        WHERE threshold_points IS NOT NULL
    LOOP
        IF v_total_points >= v_badge.threshold_points THEN
            INSERT INTO badge_awards (user_id, badge_id, awarded_at)
            SELECT NEW.user_id, v_badge.badge_id, NOW()
            WHERE NOT EXISTS (
                SELECT 1
                FROM badge_awards
                WHERE user_id = NEW.user_id
                  AND badge_id = v_badge.badge_id
            );
        END IF;
    END LOOP;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_ledger_to_badge ON points_ledger;
CREATE TRIGGER trg_ledger_to_badge
AFTER INSERT ON points_ledger
FOR EACH ROW
EXECUTE FUNCTION fn_check_badge_after_ledger();


COMMIT;