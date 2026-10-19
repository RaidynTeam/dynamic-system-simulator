# Dört kişilik Lab 1 geliştirme paketi

Hazırlanma: 19 Ekim 2026. Bu klasör uygulama kodu değil, ekip ve ajan çalışma rehberlerini içerir.

## Dağıtım

| Kişi | Gönderilecek tek dosya | Ana görev |
|---|---|---|
| 1 | [01-analitik-cozumler.md](01-analitik-cozumler.md) | Analitik çözüm, model ve ortak tipler |
| 2 | [02-sayisal-yontemler.md](02-sayisal-yontemler.md) | Euler, RK4, zaman ızgarası ve CI |
| 3 | [03-kullanici-arayuzu.md](03-kullanici-arayuzu.md) | PySide6, controller ve entegrasyon |
| 4 | [04-gorsellestirme-analiz.md](04-gorsellestirme-analiz.md) | Grafik, hata analizi ve export |

Her rehber kendi içinde ortak bağlamı, API'yi, çalışma kurallarını ve ajana talimatları içerir. Arkadaşına yalnız kendi rehberini göndermen yeterli. Markdown düz metindir; çoğu ajana dosya olarak yüklenebilir veya tamamı yapıştırılabilir.

Ajana gönderilecek başlangıç mesajı:

> Ekli rehber benim proje rolüm. Önce tamamını ve mevcut depoyu incele. Rolümü, dosya sınırlarımı ve sıradaki aşamayı özetle; M1 ile başla. Ortak sözleşmeye uy, doğrulanmamış lab koşullarını uydurma ve yaptığın değişiklikleri bana açıklayarak ilerle.

## Başlangıç ve iş yükü

Her rol yaklaşık 16 göreli iş puanı taşır. Bu eşit süre garantisi değildir; M2 sonunda gerçek ilerleme değerlendirilir. Yardım gerektiğinde önce review/test desteği paylaşılır; dosya sahipliği ve API sessizce değiştirilmez.

1. İsimleri rollere eşleyin; asıl lab yönergesini ortak depoya koyun.
2. Kişi 1 ortak sözleşmeyi, Kişi 2 paket iskeletini küçük başlangıç PR'larıyla hazırlar.
3. Kişi 3 ekran taslağını, Kişi 4 örnek eğri/Figure tasarımını aynı anda ilerletir.
4. Ortak tipler birleştikten sonra herkes aynı API üzerinden kendi M1–M3 adımlarını sürdürür.
5. M4'te gerçek verilerle entegrasyon yapılır; M5'te kanıt, ortak rapor ve savunma hazırlığı tamamlanır.

## Önerilen takvim

| Yerel tarih | Hedef |
|---|---|
| 19–20 Ekim | Yönerge eşleştirme, sözleşme, paket, M1 |
| 21 Ekim | M2 |
| 22 Ekim | M3 |
| 23–24 Ekim | M4 ve entegrasyon |
| 25 Ekim | M5, ortak rapor, görseller ve teslim paketi |

Takvim ekip önerisidir. PDF artık docs/reference altında mevcuttur: teslim **26 Ekim 2026 08.00**, üç Case, 5–6 ekran görüntüsü ve %60 savunma ağırlığı doğrulanmıştır. Ortak API v0.2 kullanılır.

## Ortak raporun birleştirilmesi

Kişi 1 model ve türetimi; Kişi 2 algoritma ve yakınsama tablosunu; Kişi 3 kullanım/entegrasyon kanıtlarını; Kişi 4 grafik/metrik yorumlarını hazırlar. Herkes kendi sonucunun kaynağını ve testini doğrular. Birleştirme ve son okuma dört kişinin ortak işidir; bu iç rehberler hocaya teslim edilecek deney raporunun yerine geçmez.

## Sözleşme bakımı

`ORTAK-SOZLESME-v0.2.md` ortak metnin bağımsız kopyasıdır. API değiştiğinde sürüm artırılır ve dört rehberdeki ortak metin birlikte güncellenir. Mevcut depo farklı bir sözleşme kullanıyorsa önce farklar kaydedilir; bu plan körlemesine uygulanmaz.

GitHub'a dosya yükleme, Issue açma, workflow etkinleştirme veya uygulama kodu geliştirme bu paketin hazırlanması sırasında yapılmadı.
