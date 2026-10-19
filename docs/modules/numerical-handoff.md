# Sayısal yöntemler teslim kaydı

Bu kayıt Kişi 2'nin M5 teslimini ve kalan ekip bağımlılıklarını gösterir.
Ödev koşulları yalnız **Lab1 RTS 09102026.doc** dosyasından alınmıştır.
Kontrol tabanı: `bf033de` (19 Ekim 2026). Rapor dili İngilizce;
öğrenciye Türkçe anlatım kullanıcının isteğiyle sonraya bırakılmıştır.

## Hazır olan katkılar

- [x] M1: ortak zaman ızgarası ve paket kurulumu.
- [x] M2: Word (15)'e uygun Euler çözümü.
- [x] M3: Word (18)-(19)'a uygun RK4 çözümü.
- [x] M4: 58 sayısal test, yakınsama ve adım yarılama deneyleri.
- [x] Kod PR #10 ile main'e alındı; main `2b51883` için Windows/Python 3.11
  [CI başarılı](https://github.com/RaidynTeam/dynamic-system-simulator/actions/runs/39309145462).
- [x] [İngilizce rapor katkısı](../report/numerical-report.md): iş dağılımı,
  algoritma, fonksiyonlar, deney tabloları, yorum ve sonuç.
- [x] [Türkçe teknik notlar](numerical.md): formül-kod ilişkisi, elle örnek,
  kararlılık, kurulum/test komutları ve savunma soruları.
- [x] [Ölçüm kaydı](../evidence/numerical-experiments.md),
  [test kaydı](../evidence/numerical-tests.txt) ve
  [ortam sürümleri](../evidence/numerical-environment.txt).

İngilizce katkı, ortak raporun tasarım, uygulama, deney ve sonuç bölümlerine
dağıtılabilir. Tam ekip raporu değildir; kapak, öğrenci bilgileri, diğer
üyelerin bölümleri ve gerçek ekran görüntüleri ortak raporda birleştirilecektir.
Ölçümler, bu dosyanın veya diğer rehberlerin varsayımları değil çalıştırılmış
betiğin çıktılarıdır. 0.01 eşik, b0=1, bitiş 20 ve t=2 yakınsama deneyi bizim
tercihlerimizdir; Word'ün zorunlu sayısal değerleri olarak sunulmayacaktır.

## Gerçek ekran görüntüleri için altı senaryo

Word 5-6 çalışan uygulama görüntüsü ister. Aşağıdaki altı senaryo bir ekip
önerisidir; görüntüler henüz çekilmedi. Her senaryoda a0=b0=1, t0=0,
t_end=20 ve analitik/Euler/RK4 birlikte seçilir. `h0=0.1*2*pi` kullanılır.
Küçük adım denenirken arayüzdeki otomatik adım seçimi kullanıcı değerini
yeniden başlangıç değerine çevirmemelidir.

| Görüntü | Case / a1 | Adım | Euler max hata | RK4 max hata |
|---|---|---|---:|---:|
| 1 | Case 1 / 1 | h0 = 0.6283185307 | 4.2456625100e-1 | 1.1940059470e-3 |
| 2 | Case 1 / 1 | h0/32 = 0.0196349541 | 7.7908424168e-3 | 9.7515684416e-10 |
| 3 | Case 2 / 2 | h0 = 0.6283185307 | 1.3645129660e-1 | 2.8790463888e-3 |
| 4 | Case 2 / 2 | h0/16 = 0.0392699082 | 6.1668402676e-3 | 2.3812393501e-8 |
| 5 | Case 3 / 3 | h0 = 0.6283185307 | 1.1290948247e-1 | 1.3349999881e-2 |
| 6 | Case 3 / 3 | h0/8 = 0.0785398163 | 6.4584911355e-3 | 1.1100609671e-6 |

Tablodaki ölçümler betiğin tam hassasiyetli h değerlerinden gelir. Ekranda
yuvarlatılmış adım girilirse son basamaklar değişebilir. Görüntülerde giriş
parametreleri, kullanılan adım, yöntem etiketleri, eksenler ve gerçek sonuçlar
okunabilir olmalıdır. Örnek/demo veriyi veya boş grafik alanını doğruluk kanıtı
olarak kullanmayın. Hata metriği referansla aynı zaman örneklerinden üretilmelidir.

## Kişi 4 incelemesi ve ekip bağımlılıkları

- [ ] Kişi 4'ün grafik PR'ını inceleme. Kontrol anında ilgili PR bulunmadı;
  `visualization` modülleri boş. İnceleme yapılmış gibi işaretlenmedi.
- [ ] Kişi 3'ün controller üzerinden gerçek çözücü ve grafik entegrasyonu.
  Kontrol tabanında `run_simulation` hâlâ `NotImplementedError` veriyor.
- [ ] Gerçek uygulamadan 5-6 ekran görüntüsü; önerilen senaryolar yukarıda.
- [ ] Ortak raporu birleştirme, rapor çıktısı ve kaynak/çalıştırılabilir dosyalarla
  RAR teslim paketini hazırlama. Çalıştırılabilir teslim biçimi ekipçe
  netleştirilecek; yalnız kaynak dosyaların bunu karşıladığı varsayılmayacak.
- [ ] Türkçe anlatım ve sözlü savunma provası; kullanıcı isteğiyle ertelendi.

Kişi 4'ün PR'ı geldiğinde şu kontroller yapılacak: gerçek Response verisinin
çizilmesi, aynı t dizilerinin kullanılması, maksimum hata/RMSE hesabının
doğruluğu, doğru yöntem etiketleri ve eksenler, PNG/PDF çıktılarının okunabilirliği.
İlgili PR gelmeden onay veya başarılı inceleme kaydı oluşturulmayacak.

## Durum özeti

Kişi 2'nin sayısal kodu, testleri ve rapor katkısı hazırdır. M5'in teknik
dokümantasyon kısmı tamamdır; Kişi 4 incelemesi beklemede ve sözlü hazırlık
ertelenmiştir. Bu durum, bütün uygulamanın veya ortak teslimin tamamlandığı
anlamına gelmez. Word'e göre teslim 26 Ekim 2026 Pazartesi 08.00;
notlandırma %40 rapor ve %60 uygulamayı açıklamadır.
