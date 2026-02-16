# Kanaka Login İşlemi Testi

## Yapılan Değişiklikler

### 1. **Kanaka Kullanıcısı Eklendi**
- ✅ `/datasets/users.csv` → `U6,Kanaka,Istanbul,STUDENT` eklendi
- ✅ `/datasets/user_state.csv` → Kanaka için 0'lı başlangıç satırı eklendi
- ✅ `/datasets/activity_events.csv` → Kanaka için son 5 gün etkinlik verileri eklendi

### 2. **Activity API Düzeltildi**
- ✅ `backend/app/controllers/activity.py` → `record_login` şimdi POST body'den `user_id` okuyor
- ✅ LoginRequest Pydantic modeli eklendi
- ✅ Hem body hem de query parameter desteği (geriye dönük uyum)

### 3. **Frontend API Çağrısı Güzellendi**
- ✅ `frontend/js/api.js` → `recordLogin()` artık user_id'yi JSON body'de gönderiyor
- ✅ `frontend/js/app.js` → Login sonrası pipeline triggerı ve dashboard refresh'i iyileştirildi
- ✅ Error handling ve status checks iyileştirildi

### 4. **Database Tarihleri Güncellendi**
- ✅ activity_events.csv → Tarihler 2026-02-08 hingga 2026-02-16 olarak ayarlandı
- ✅ Mevcut tarih (2026-02-17) çerçevesinde doğru veriler sağlanıyor

## Test Adımları

1. **Database İlk Kurulumu**
   ```bash
   cd /Users/beratzengin/Desktop/TurkcellBootcamp/backend
   python -m scripts.setup_data
   ```

2. **Backend Başlat**
   ```bash
   cd backend
   uvicorn app.main:app --reload
   ```

3. **Frontend Başlat** (ayrı terminal)
   ```bash
   cd frontend
   python -m http.server 5173
   ```

4. **Tarayıcıda Deneyin**
   - URL: http://localhost:5173
   - Giriş yap: "Kanaka" veya "U6"
   - 🔔 Bildirim görülmeli: "Giriş kaydedildi"
   - ⏳ 1-2 saniye bekle (pipeline çalışıyor)
   - 📊 Dashboard gösterilmeli güncellenmiş verilerle

## Beklenen Sonuçlar

✅ **Kanaka kullanıcısı bulunacak** (users.csv'de var)
✅ **Activity event kaydedilecek** (activity_events tablosuna INSERT)
✅ **Pipeline çalışacak** (activity_events → user_state hesaplayacak)
✅ **Dashboard güncellendi gösterilecek** (yeni puan, streak, vb)
✅ **Leaderboard güncellenecek** (total_points hesaplanacak)

## Console'dan Test
```bash
curl -X POST 'http://localhost:8000/activity/record-login' \
  -H 'Content-Type: application/json' \
  -d '{"user_id":"U6"}'

# Yanıt:
# {"status": "success", "message": "...", "user_id": "U6", ...}
```

## Sorun Bildir
Eğer hala çalışmıyorsa:
1. Backend logs'unu kontrol et
2. Database bağlantısını doğrula: `psql YOUR_DB`
3. `SELECT COUNT(*) FROM users;` - U6 var mı?
4. `SELECT COUNT(*) FROM activity_events WHERE date >= '2026-02-12';` - Kanaka data var mı?
