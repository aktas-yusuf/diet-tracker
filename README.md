# Diet Tracker

Django tabanlı diyet takip ve öneri uygulaması.

## Özellikler

- Kullanıcı kayıt ve giriş sistemi
- Diyet önerileri
- Kullanıcı profilleri
- SQLite veritabanı

## Kurulum

1. Repository'yi klonlayın:
```bash
git clone https://github.com/aktayusuf/diet-tracker.git
cd diet-tracker
```

2. Bağımlılıkları yükleyin:
```bash
pip install -r requirements.txt
```

3. Migrasyonları çalıştırın:
```bash
python manage.py migrate
```

4. Sunucuyu başlatın:
```bash
python manage.py runserver
```

## Kullanım

Tarayıcınızda `http://localhost:8000` adresine gidin.