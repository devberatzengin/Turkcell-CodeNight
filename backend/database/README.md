Bu klasör backend için veritabanı başlangıç (init) yardımcı dosyalarını içerir.

Önkoşullar
- Postgres konteyneri/servisi çalışıyor (Docker veya local)
- `backend/.env` dosyasındaki `DATABASE_URL` doğru ayarlı

Başlatma adımları

1. `backend/.env` dosyasındaki `DATABASE_URL` değerini kendi Docker/Postgres bağlantınıza göre güncelleyin.
   Örnek (SQLAlchemy format): `postgresql://username:password@localhost:5433/turkcell_db`

2. Şemayı manuel olarak uygulamak için `psql` veya Docker kullanabilirsiniz. Örnekler:

```bash
# using psql locally
psql "$DATABASE_URL" -f gamification_database.sql

# or via docker (adjust network/host settings as needed)
docker run --rm -v "$PWD:/workspace" --network host postgres:15 bash -c \
  "psql '$DATABASE_URL' -f /workspace/gamification_database.sql"
```

Not: Bu repo artık otomatik `init.sh` çalıştırmaz; şemayı el ile veya CI/deploy adımında uygulamanız beklenir.
