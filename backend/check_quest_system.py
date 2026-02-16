"""Script to verify quest earn system with triggers and badges."""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app import db
from sqlalchemy import text

def check_system():
    print("=" * 60)
    print("QUEST EARN SİSTEM KONTROLÜ")
    print("=" * 60)
    
    with db.engine.connect() as conn:
        # 1. Badge threshold kontrolü
        print("\n1️⃣ BADGE THRESHOLD AYARLARI:")
        print("-" * 60)
        badges = conn.execute(text("""
            SELECT badge_id, badge_name, threshold_points 
            FROM badges 
            ORDER BY threshold_points
        """)).fetchall()
        
        for b in badges:
            print(f"  {b[0]}: {b[1]:20s} → {b[2]:5} puan")
        
        # 2. Trigger kontrolü
        print("\n2️⃣ DATABASE TRIGGER KONTROLÜ:")
        print("-" * 60)
        triggers = conn.execute(text("""
            SELECT trigger_name, event_object_table, action_statement 
            FROM information_schema.triggers 
            WHERE trigger_schema = 'public' 
            AND trigger_name IN ('trg_quest_award_to_ledger', 'trg_ledger_to_badge')
            ORDER BY trigger_name
        """)).fetchall()
        
        if triggers:
            for t in triggers:
                print(f"  ✅ {t[0]} on {t[1]}")
        else:
            print("  ⚠️  Trigger'lar bulunamadı!")
        
        # 3. Örnek kullanıcı puanları
        print("\n3️⃣ ÖRNEK KULLANICILAR VE PUANLARI:")
        print("-" * 60)
        users = conn.execute(text("""
            SELECT u.user_id, u.name, 
                   COALESCE(lv.total_points, 0) as total_points,
                   COALESCE(lv.rank, 999) as rank
            FROM users u
            LEFT JOIN leaderboard_view lv ON u.user_id = lv.user_id
            ORDER BY total_points DESC
            LIMIT 10
        """)).fetchall()
        
        for u in users:
            # Badge kontrolü
            badges = conn.execute(text("""
                SELECT b.badge_name 
                FROM badge_awards ba
                JOIN badges b ON ba.badge_id = b.badge_id
                WHERE ba.user_id = :u
            """), {'u': u[0]}).fetchall()
            
            badge_names = ', '.join([b[0] for b in badges]) if badges else "Yok"
            print(f"  {u[0]}: {u[1]:15s} | {u[2]:4d} puan | Rank #{u[3]} | Rozetler: {badge_names}")
        
        # 4. Aktif quest'ler
        print("\n4️⃣ AKTİF QUEST'LER:")
        print("-" * 60)
        quests = conn.execute(text("""
            SELECT quest_id, quest_name, reward_points, priority
            FROM quests
            WHERE is_active = true
            ORDER BY priority
        """)).fetchall()
        
        for q in quests:
            print(f"  {q[0]}: {q[1]:30s} | {q[2]:3d} puan | Priority: {q[3]}")
        
        # 5. Son quest awards
        print("\n5️⃣ SON QUEST KAZANIMLARI:")
        print("-" * 60)
        awards = conn.execute(text("""
            SELECT qa.user_id, u.name, qa.selected_quest, qa.reward_points, qa.timestamp
            FROM quest_awards qa
            JOIN users u ON qa.user_id = u.user_id
            ORDER BY qa.timestamp DESC
            LIMIT 5
        """)).fetchall()
        
        if awards:
            for a in awards:
                print(f"  {a[0]} ({a[1]}): {a[2]} → +{a[3]} puan @ {a[4]}")
        else:
            print("  Henüz kazanım yok")
        
        print("\n" + "=" * 60)
        print("SİSTEM AKIŞI:")
        print("=" * 60)
        print("1. Quest Earn → quest_awards INSERT")
        print("2. [TRIGGER] quest_awards → points_ledger INSERT")
        print("3. [TRIGGER] points_ledger → badge_awards kontrol/INSERT")
        print("4. [VIEW] leaderboard_view otomatik güncelleme")
        print("=" * 60)

if __name__ == "__main__":
    try:
        check_system()
    except Exception as e:
        print(f"\n❌ HATA: {e}")
        import traceback
        traceback.print_exc()
