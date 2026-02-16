"""Test badge notification with a fresh quest earn."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app import db
from sqlalchemy import text
from datetime import datetime
import uuid

def test_badge_notification():
    print("=" * 60)
    print("BADGE BİLDİRİM TESTİ - YENİ BADGE KAZANMA")
    print("=" * 60)
    
    with db.engine.connect() as conn:
        # Düşük puanlı, badge kazanabilecek bir kullanıcı bul
        user = conn.execute(text("""
            SELECT u.user_id, u.name, 
                   COALESCE(lv.total_points, 0) as total_points,
                   (SELECT COUNT(*) FROM badge_awards WHERE user_id = u.user_id) as badge_count
            FROM users u
            LEFT JOIN leaderboard_view lv ON u.user_id = lv.user_id
            WHERE COALESCE(lv.total_points, 0) < 1500
            ORDER BY total_points ASC
            LIMIT 1
        """)).fetchone()
        
        if not user:
            print("❌ Uygun kullanıcı bulunamadı!")
            return
        
        user_id, user_name, current_points, badge_count = user[0], user[1], user[2], user[3]
        
        print(f"\n📊 Test Kullanıcısı: {user_name} ({user_id})")
        print(f"   Mevcut Puan: {current_points}")
        print(f"   Mevcut Badge Sayısı: {badge_count}")
        
        # Mevcut rozetler
        current_badges = conn.execute(text("""
            SELECT b.badge_name
            FROM badge_awards ba
            JOIN badges b ON ba.badge_id = b.badge_id
            WHERE ba.user_id = :u
        """), {'u': user_id}).fetchall()
        
        print(f"   Rozetler: {', '.join([b[0] for b in current_badges]) if current_badges else 'Yok'}")
        
        # Yüksek puanlı quest bul
        quest = conn.execute(text("""
            SELECT quest_id, quest_name, reward_points
            FROM quests
            WHERE is_active = true AND reward_points >= 400
            ORDER BY reward_points DESC
            LIMIT 1
        """)).fetchone()
        
        if not quest:
            print("❌ Yüksek puanlı quest bulunamadı!")
            return
        
        quest_id, quest_name, reward_points = quest[0], quest[1], quest[2]
        new_total = current_points + reward_points
        
        print(f"\n🎯 Kazanılacak Quest: {quest_name} (+{reward_points} puan)")
        print(f"   Yeni Toplam: {new_total} puan")
        
        # Hangi badge'leri kazanacak?
        print(f"\n🏆 Badge Tahmini:")
        thresholds = conn.execute(text("""
            SELECT badge_id, badge_name, threshold_points
            FROM badges
            WHERE threshold_points IS NOT NULL
            ORDER BY threshold_points
        """)).fetchall()
        
        will_earn_badges = []
        for b in thresholds:
            badge_id, badge_name, threshold = b[0], b[1], b[2]
            has_badge = any(cb[0] == badge_name for cb in current_badges)
            
            if new_total >= threshold and not has_badge:
                will_earn_badges.append(badge_name)
                print(f"   ✅ {badge_name} ({threshold} puan) KAZANILACAK!")
            elif has_badge:
                print(f"   ✓ {badge_name} (zaten var)")
            else:
                print(f"   ❌ {badge_name} ({threshold - new_total} puan eksik)")
        
        if not will_earn_badges:
            print("\n⚠️  Bu quest ile yeni badge kazanılmayacak!")
            return
    
    print("\n" + "=" * 60)
    print(f"🚀 Quest kazandırılıyor ve badge bildirimi test ediliyor...")
    print("=" * 60)
    
    # Quest'i kazandır
    with db.engine.begin() as conn:
        award_id = f"QA-BADGE-TEST-{uuid.uuid4().hex[:6]}"
        ts = datetime.utcnow()
        
        # Quest award + junction
        conn.execute(text("""
            INSERT INTO quest_awards (award_id, user_id, as_of_date, selected_quest, reward_points, timestamp)
            VALUES (:a, :u, CURRENT_DATE, :q, :p, :ts)
        """), {'a': award_id, 'u': user_id, 'q': quest_id, 'p': reward_points, 'ts': ts})
        
        conn.execute(text("""
            INSERT INTO quest_award_quests (award_id, quest_id, status)
            VALUES (:a, :q, 'TRIGGERED')
        """), {'a': award_id, 'q': quest_id})
        
        # Quest notification
        quest_notif_id = f"N-QUEST-{uuid.uuid4().hex[:6]}"
        conn.execute(text("""
            INSERT INTO notifications (notification_id, user_id, channel, message, sent_at)
            VALUES (:n, :u, 'BiP', :m, :ts)
        """), {
            'n': quest_notif_id,
            'u': user_id,
            'm': f"🎉 Başarılı! '{quest_name}' görevi tamamlandı. +{reward_points} puan!",
            'ts': ts
        })
        
        print(f"\n✅ Quest kazandırıldı (Award ID: {award_id})")
        
    # Trigger'lar otomatik çalıştı, sonuçları kontrol et
    with db.engine.connect() as conn:
        # Ledger kontrol
        ledger = conn.execute(text("""
            SELECT ledger_id, points_delta, created_at
            FROM points_ledger
            WHERE user_id = :u AND source_ref = :a
        """), {'u': user_id, 'a': award_id}).fetchone()
        
        if ledger:
            print(f"✅ Ledger eklendi: {ledger[0]} (+{ledger[1]} puan)")
        else:
            print("❌ Ledger eklenmedi!")
            
        # Badge awards kontrol
        new_badges = conn.execute(text("""
            SELECT b.badge_name, ba.awarded_at
            FROM badge_awards ba
            JOIN badges b ON ba.badge_id = b.badge_id
            WHERE ba.user_id = :u
            ORDER BY ba.awarded_at DESC
            LIMIT 3
        """), {'u': user_id}).fetchall()
        
        print(f"\n🏆 Badge Durumu:")
        for nb in new_badges:
            print(f"   {nb[0]} @ {nb[1]}")
        
        # Bildirimler kontrol
        print(f"\n📬 Son Bildirimler:")
        notifications = conn.execute(text("""
            SELECT notification_id, message, sent_at
            FROM notifications
            WHERE user_id = :u
            ORDER BY sent_at DESC
            LIMIT 5
        """), {'u': user_id}).fetchall()
        
        badge_notifications = 0
        for n in notifications:
            is_badge = '🏆' in n[1] or 'rozet' in n[1]
            marker = "🏆" if is_badge else "📝"
            print(f"   {marker} {n[1]}")
            if is_badge:
                badge_notifications += 1
        
        # Final durum
        final_points = conn.execute(text("""
            SELECT COALESCE(SUM(points_delta), 0)
            FROM points_ledger
            WHERE user_id = :u
        """), {'u': user_id}).scalar()
        
        print(f"\n📊 Final Durum:")
        print(f"   Toplam Puan: {final_points}")
        print(f"   Badge Bildirimleri: {badge_notifications}")
        
        if badge_notifications > 0:
            print("\n✅ BAŞARILI! Badge bildirimleri gönderildi! 🎉")
        else:
            print("\n❌ SORUN VAR! Badge bildirimi gönderilmedi!")
        
        print("=" * 60)

if __name__ == "__main__":
    try:
        test_badge_notification()
    except Exception as e:
        print(f"\n❌ HATA: {e}")
        import traceback
        traceback.print_exc()
