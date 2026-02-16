"""Update badge trigger to send notifications when badges are awarded."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app import db
from sqlalchemy import text

def update_trigger():
    print("=" * 60)
    print("BADGE TRIGGER GÜNCELLEME - BİLDİRİM EKLENİYOR")
    print("=" * 60)
    
    trigger_sql = """
CREATE OR REPLACE FUNCTION fn_check_badge_after_ledger()
RETURNS TRIGGER AS $$
DECLARE
    v_total_points INTEGER;
    v_badge RECORD;
    v_badge_name TEXT;
    v_notif_id TEXT;
    v_badge_inserted BOOLEAN;
BEGIN
    -- Güncel toplam puanı ledger'dan hesapla
    SELECT COALESCE(SUM(points_delta),0)
    INTO v_total_points
    FROM points_ledger
    WHERE user_id = NEW.user_id;

    -- Threshold'a göre badge kontrolü
    FOR v_badge IN
        SELECT badge_id, badge_name, threshold_points
        FROM badges
        WHERE threshold_points IS NOT NULL
        ORDER BY threshold_points
    LOOP
        IF v_total_points >= v_badge.threshold_points THEN
            -- Badge'i ekle (zaten varsa ekleme)
            v_badge_inserted := FALSE;
            
            INSERT INTO badge_awards (user_id, badge_id, awarded_at)
            SELECT NEW.user_id, v_badge.badge_id, NOW()
            WHERE NOT EXISTS (
                SELECT 1
                FROM badge_awards
                WHERE user_id = NEW.user_id
                  AND badge_id = v_badge.badge_id
            );
            
            -- Eğer yeni badge eklendiyse bildirim gönder
            IF FOUND THEN
                v_badge_inserted := TRUE;
                v_notif_id := CONCAT('N-BADGE-', substr(md5(random()::text), 1, 8), '-', NEW.user_id);
                
                INSERT INTO notifications (notification_id, user_id, channel, message, sent_at)
                VALUES (
                    v_notif_id,
                    NEW.user_id,
                    'BiP',
                    CONCAT('🏆 Tebrikler! "', v_badge.badge_name, '" rozetini kazandınız! (', v_total_points, ' puan)'),
                    NOW()
                );
            END IF;
        END IF;
    END LOOP;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
    """
    
    try:
        with db.engine.begin() as conn:
            print("\n✅ Trigger fonksiyonu güncelleniyor...")
            conn.execute(text(trigger_sql))
            print("✅ Trigger başarıyla güncellendi!")
            
            print("\n📋 Trigger durumu:")
            triggers = conn.execute(text("""
                SELECT trigger_name, event_object_table 
                FROM information_schema.triggers 
                WHERE trigger_schema = 'public' 
                AND trigger_name = 'trg_ledger_to_badge'
            """)).fetchall()
            
            for t in triggers:
                print(f"  ✅ {t[0]} on {t[1]}")
            
            print("\n" + "=" * 60)
            print("YENİ ÖZELLİK:")
            print("=" * 60)
            print("Artık badge kazanıldığında otomatik bildirim gönderilecek!")
            print("Örnek: '🏆 Tebrikler! \"Bronz Oyuncu\" rozetini kazandınız! (350 puan)'")
            print("=" * 60)
            
    except Exception as e:
        print(f"\n❌ HATA: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    update_trigger()
