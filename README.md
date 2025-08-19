Diet Tracker - Akıllı Diyet Takip Uygulaması

Modern web teknolojileri kullanılarak geliştirilmiş, yapay zeka destekli kişiselleştirilmiş diyet önerileri sunan Django tabanlı web uygulaması.



Kullanıcı Yönetimi
Gelişmiş Kullanıcı Kayıt Sistemi: Email tabanlı kimlik doğrulama
Kapsamlı Profil Sistemi: Yaş, kilo, boy, cinsiyet, aktivite seviyesi
Güvenli Giriş/Çıkış: Django authentication sistemi
Profil Güncelleme: Kullanıcı bilgilerini düzenleme

Akıllı Diyet Önerileri
Kişiselleştirilmiş Kalori Hesaplama: Mifflin-St Jeor formülü ile BMR hesaplama
Aktivite Seviyesi Bazlı Öneriler: Düşük, orta, yüksek aktivite seviyeleri
BMI Hesaplama ve Kategorilendirme: Zayıf, normal, fazla kilolu, obez
Makro Besin Oranları: Protein, karbonhidrat, yağ dağılımı
Günlük Beslenme Planı: Öğün bazlı kalori dağılımı

Edamam Food Database API Entegrasyonu
Gerçek Zamanlı Yemek Arama: 100,000+ yemek veritabanı
Besin Değeri Analizi: Kalori, protein, karbonhidrat, yağ bilgileri
Akıllı Filtreleme: Kalori aralığına göre yemek önerileri
Cache Sistemi: API çağrılarını optimize etme
Çoklu Dil Desteği: İngilizce ve Türkçe yemek isimleri

Beslenme Analizi
Günlük Kalori İhtiyacı: Kişisel metabolizma hızına göre hesaplama
Beslenme Tavsiyeleri: Uzman önerileri ve ipuçları
Kalori Takibi: Hedef vs. gerçekleşen kalori karşılaştırması
Öneri Geçmişi: Kullanıcının aldığı önerileri kaydetme

Teknoloji Stack
 Backend
Django 5.2.4: Modern Python web framework
Python 3.8+: Güçlü programlama dili
SQLite3: Hafif ve hızlı veritabanı
Django ORM: Veritabanı yönetimi
Django Authentication: Güvenli kullanıcı yönetimi

Frontend
HTML5: Semantik markup
CSS3: Modern styling ve responsive design
JavaScript: Dinamik kullanıcı etkileşimi
Bootstrap: Responsive UI framework
Django Templates: Server-side rendering

API ve Entegrasyon
Edamam Food Database API: Yemek ve besin değeri verileri
RESTful API: Modern web servis mimarisi
HTTP Requests: Python requests kütüphanesi
JSON Parsing: Veri işleme ve dönüştürme

Veritabanı ve Cache
SQLite3: Geliştirme ve test veritabanı
Django Cache Framework: Performans optimizasyonu
Database Migrations: Veritabanı şema yönetimi

Güvenlik
CSRF Protection: Cross-site request forgery koruması
SQL Injection Protection: Django ORM güvenliği
Password Validation: Güçlü şifre doğrulama
Session Management: Güvenli oturum yönetimi

Gereksinimler
Python: 3.8 veya üzeri
pip: Python paket yöneticisi
Git: Versiyon kontrol sistemi
Edamam API Keys**: Food Database erişimi için

Kurulum
Repository'yi Klonlayın
```bash
git clone https://github.com/aktayusuf/diet-tracker.git
cd diet-tracker
```
Sanal Ortam Oluşturun
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

Bağımlılıkları Yükleyin
```bash
pip install -r requirements.txt
```

Edamam API Anahtarlarını Ayarlayın
`diet_tracker/settings.py` dosyasında:
```python
EDAMAM_APP_ID = 'your_app_id_here'
EDAMAM_APP_KEY = 'your_app_key_here'
```

[Edamam Developer Portal](https://developer.edamam.com/edamam-food-database-api) adresinden ücretsiz API anahtarları alabilirsiniz.

 Veritabanı Migrasyonlarını Çalıştırın
```bash
python manage.py migrate
```

Süper Kullanıcı Oluşturun (İsteğe Bağlı)
```bash
python manage.py createsuperuser
```
 Geliştirme Sunucusunu Başlatın
```bash
python manage.py runserver
```

Uygulamaya Erişin
Tarayıcınızda `http://localhost:8000` adresine gidin

Kullanım
İlk Kullanım
1Kayıt Olun**: Email ve kullanıcı adı ile hesap oluşturun
Profilinizi Tamamlayın**: Yaş, kilo, boy, cinsiyet, aktivite seviyesi
Diyet Önerisi Alın**: Kişiselleştirilmiş beslenme planı

Diyet Önerileri
Kalori Hesaplama**: Kişisel metabolizma hızınıza göre
Yemek Önerileri**: Edamam API'den gerçek zamanlı veriler
Besin Değeri Analizi**: Detaylı makro besin bilgileri
Özelleştirilmiş Planlar**: Hedeflerinize uygun beslenme

Takip ve Analiz
Günlük Kalori Takibi: Hedef vs. gerçekleşen
BMI Kategorisi**: Sağlık durumu analizi
Beslenme Tavsiyeleri**: Uzman önerileri
Öneri Geçmişi**: Geçmiş diyet planlarınız

 Proje Yapısı
