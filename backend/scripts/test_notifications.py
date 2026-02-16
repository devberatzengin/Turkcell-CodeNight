"""Test notification system for quest earn and badge awards."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app import db
from sqlalchemy import text
from datetime import datetime
import uuid

def test_quest_earn_with_notifications():
    print("=" * 60)
    print("QUEST EARN VE BADGE BİLDİRİM TESTİ")
    print("=" * 60)
    
    # Test için bir kullanıcı seç (düşük puanlı)
    with db.engine.connect() as conn:
        user = conn.execute(text("""
            SELECT u.user_id, u.name, COALESCE(lv.total_points, 0) as total_points
            FROM users u
            LEFT JOIN leaderboard_view lv ON u.user_id = lv.user_id
            ORDER BY total_points ASC
            LIMIT 1
        """)).fetchone()
        
        if not user:
            print("❌ Kullanıcı bulunamadı!")
            return
        
        user_id = user[0]
        user_name = user[1]
        current_points = user[2]
        
        print(f"\n📊 Test Kullanıcısı:")
        print(f"   User ID: {user_id}")
        print(f"   İsim: {user_name}")
        print(f"   Mevcut Puan: {current_points}")
        
        # Mevcut rozetleri göster
        badges = conn.execute(text("""
            SELECT b.badge_name 
            FROM badge_awards ba
            JOIN badges b ON ba.badge_id = b.badge_id
            WHERE ba.user_id = :u
        """), {'u': user_id}).fetchall()
        
        badge_names = [b[0] for b in badges]
        print(f"   Mevcut Rozetler: {', '.join(badge_names) if badge_names else 'Yok'}")
        
        # Hangi quest'i kazanacağını belirle (yüksek puanlı)
        quest = conn.execute(text("""
            SELECT quest_id, quest_name, reward_points
            FROM quests
            WHERE is_active = true AND reward_points > 0
            ORDER BY reward_points DESC
            LIMIT 1
        """)).fetchone()
        
        if not quest:
            print("❌ Aktif quest bulunamadı!")
            return
        
        quest_id = quest[0]
        quest_name = quest[1]
        reward_points = quest[2]
        
        new_total = current_points + reward_points
        
        print(f"\n🎯 Kazanılacak Quest:")
        print(f"   Quest ID: {quest_id}")
        print(f"   İsim: {quest_name}")
        print(f"   Ödül: {reward_points} puan")
        print(f"   Yeni Toplam: {new_total} puan")
        
        # Badge threshold kontrolü
        print(f"\n🏆 Badge Durumu:")
        thresholds = conn.execute(text("""
            SELECT badge_id, badge_name, threshold_points
            FROM badges
            WHERE threshold_points IS NOT NULL
            ORDER BY threshold_points
        """)).fetchall()
        
        for b in thresholds:
            badge_id, badge_name, threshold = b[0], b[1], b[2]
            has_badge = badge_id in [ba[0] for ba in conn.execute(text("""
                SELECT badge_id FROM badge_awards WHERE user_id = :u
            """), {'u': user_id}).fetchall()]
            
            will_earn = new_total >= threshold and not has_badge
            status = "✅ KAZANILACAK!" if will_earn else ("✓ Var" if has_badge else f"({threshold - new_total} puan kaldı)")
            print(f"   {badge_name} ({threshold} puan): {status}")
    
    # Kullanıcıya sor
    print("\n" + "=" * 60)
    response = input(f"Quest kazandırmak ister misiniz? (y/n): ").strip().lower()
    
    if response != 'y':
        print("❌ İşlem iptal edildi.")
        return
    
    # Quest'i kazandır
    with db.engine.begin() as conn:
        award_id = f"QA-TEST-{uuid.uuid4().hex[:8]}-{user_id}"
        ts = datetime.utcnow()
        
        # Quest award ekle
        conn.execute(text("""
            INSERT INTO quest_awards (award_id, user_id, as_of_date, selected_quest, reward_points, timestamp)
            VALUES (:a, :u, CURRENT_DATE, :q, :p, :ts)
        """), {'a': award_id, 'u': user_id, 'q': quest_id, 'p': reward_points, 'ts': ts})
        
        # Junction ekle
        conn.execute(text("""
            INSERT INTO quest_award_quests (award_id, quest_id, status)
            VALUES (:a, :q, 'TRIGGERED')
        """), {'a': award_id, 'q': quest_id})
        
        # Quest notification ekle
        notif_id = f"N-QUEST-{uuid.uuid4().hex[:8]}-{user_id}"
        conn.execute(text("""
            INSERT INTO notifications (notification_id, user_id, channel, message, sent_at)
            VALUES (:n, :u, 'BiP', :m, :ts)
        """), {
            'n': notif_id,
            'u': user_id,
            'm': f"🎉 Başarılı! '{quest_name}' görevi tamamlandı. +{reward_points} puan!",
            'ts': ts
        })
        
        print(f"\n✅ Quest kazandırıldı!")
        print(f"   Award ID: {award_id}")
        print(f"   Bildiri ID: {notif_id}")
        
        # Trigger'lar otomatik çalıştı, bildirimleri kontrol et
        print(f"\n📬 Bildirimler:")
        notifications = conn.execute(text("""
            SELECT notification_id, message, sent_at
            FROM notifications
            WHERE user_id = :u
            ORDER BY sent_at DESC
            LIMIT 5
        """), {'u': user_id}).fetchall()
        
        for n in notifications:
            print(f"   [{n[2]}] {n[1]}")
        
        # Güncel durumu göster
        final_points = conn.execute(text("""
            SELECT COALESCE(SUM(points_delta), 0)
            FROM points_ledger
            WHERE user_id = :u
        """), {'u': user_id}).scalar()
        
        final_badges = conn.execute(text("""
            SELECT b.badge_name
            FROM badge_awards ba
            JOIN badges b ON ba.badge_id = b.badge_id
            WHERE ba.user_id = :u
            ORDER BY ba.awarded_at
        """), {'u': user_id}).fetchall()
        
        print(f"\n📊 Güncel Durum:")
        print(f"   Toplam Puan: {final_points}")
        print(f"   Rozetler: {', '.join([b[0] for b in final_badges])}")
        print("=" * 60)

if __name__ == "__main__":
    try:
        test_quest_earn_with_notifications()
    except Exception as e:
        print(f"\n❌ HATA: {e}")
        import traceback
        traceback.print_exc()
