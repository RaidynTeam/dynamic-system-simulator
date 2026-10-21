# Dynamic System Simulator

Lab 1 için dört kişinin geliştireceği Python proje iskeleti.

## Durum — M4B-2 real visualization integration (COMPLETE)

PySide6 uygulamasında Case veya özel katsayıları ve yöntemleri seçip Run
Simulation'a basın. Mevcut QThread controller'ı çalıştırır; yalnız geçerli güncel
sonuçlar Person 4'ün gerçek grafik/metrik API'lerine aktarılır. Response görünümü
seçili yöntemlerin gerçek y(t) eğrilerini gösterir. Exact ile Euler/RK4 birlikte
seçildiğinde Error görünümü, maksimum mutlak hata ve RMSE kullanılabilir.
Yalnız Exact veya yalnız sayısal yöntemlerde referans uydurulmaz; hata görünümü
kapalı ve metrikler Not calculated olarak kalır.

Açık/koyu tema QSettings ile korunur. Tema değişimi mevcut Responses üzerinden
iki grafiği yeniden üretir; çözücüler/metrik hesabı tekrarlanmaz ve seçili görünüm
korunur. Euler her iki temada #FF1D8D; açık eğriler Exact #475569 / RK4 #2563EB,
koyu eğriler Exact #CBD5E1 / RK4 #60A5FA kullanır. Onaylı 35/65 düzen değişmedi.

Response veya Error seçip PNG/PDF düğmesine basarak gerçek grafiği kaydedin.
İptal işlemi değiştirmez; mevcut dosya için onay istenir. Başarı yalnız gerçek,
boş olmayan dosya oluşturulduktan sonra gösterilir. DEMO veri kullanılmaz.
Hesap sırasında ikinci Run engellenir; değişen girdiler eski sonuçları geçersiz
kılar. Kapanış aktif worker bitene kadar ertelenir; iptal özelliği yoktur.
Görselleştirme hatası grafikleri temizler, kabul edilen hesap verisini korur.

Hocanın **Lab1 RTS 09102026** yönergesi geliştirme sırasında main'e eklendi:
[kaynak PDF](docs/reference/Lab1-RTS-09102026.pdf) ve
[gereksinim eşlemesi](docs/lab-requirements.md). M1 lab modeli:
`y'' + a1*y' + a0*y = b0*u(t)`,
birim basamak, sıfır başlangıç koşulları ve pozitif `a1`, `a0`, `b0`.
Case 1/2/3 sırasıyla `a1=1/2/3`, `a0=1` değerlerini seçer.
İlk `dt = 0.1 * 2*pi/sqrt(a0)`; kullanıcı daha küçük adım seçebilir.
`b0=1` ve `t_end=20 s` yalnız düzenlenebilir UI varsayılanlarıdır.
Ortak API main'de v0.2'ye güncellenmiştir: `ModelParams(a1,a0,b0)`.
UI state hem v0.2 alanlarını hem görevde istenen eski genel v0.1 alan eşlemesini
ayrı metotlarla sunar; ortak sözleşme UI tarafından değiştirilmez.

## Kurulum

Python 3.11 veya üzeri kullanın. Bu klasörde hazırlanan `.venv` yerel ortamdır ve Git'e eklenmez.

```sh
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt
python -m pip install -e .
```

Windows PowerShell kurulumu ve çalıştırma:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
.\.venv\Scripts\python.exe -m dss
```

macOS'ta bu çalışma alanı Qt dosyalarını gizli işaretleyebildiğinden uygulamayı
her zaman proje klasöründen `./run.command` ile açın. Başlatıcı bu işareti
çalıştırmadan önce otomatik düzeltir. Düzenli kullanım için doğrudan komutlar:

```sh
/usr/bin/chflags -R nohidden .venv
PYTHONPATH=src .venv/bin/python -m dss
```

Aktif Python ortamında diğer platformlarda `python -m dss` kullanın.

Örnek akış: Case 2 düğmesine basın, `b0` slider'ını ve bitiş zamanını düzenleyin,
yöntemleri seçin ve Run Simulation'a basın. Arayüz hesap sırasında kullanılabilir;
sonuçta gerçek eğriler ve uygun hata metrikleri görünür. Çalışırken girdileri
değiştirirseniz o çalışmanın sonucu atılır; yeni Run için mevcut hesabın bitmesini bekleyin.

- `a1`, `a0`, `b0`: QSlider, 0.01–20.00 aralığı, 0.01 adım ve sayısal değer etiketi.
- `dt`: logaritmik QSlider, 0.000001–10 saniye, her onluk mertebede 200 adım.
- Auto dt başlangıçta açıktır; `a0` değişince ilk lab formülü uygulanır.
  `dt` slider'ını elle değiştirmek veya `dt / 2`, `dt × 2` kullanmak Auto dt'yi kapatır.
- Case seçimi veya Auto dt'yi yeniden açmak ilk formülü uygular; `b0` korunur.
- Auto dt ve yarılama/ikiye katlama tam kayan nokta değerini korur; slider kolu
  en yakın logaritmik konumu gösterir. Hesaplamaya aktarılacak değer etikette gösterilir.
- Aralık dışı değerler önceki değeri korur ve hata mesajı verir; sessiz kırpma yapılmaz.
- Başlangıç API v0.2 gereği sıfırda sabittir; bu bilgi bitiş zamanı ipucundadır.
  Bitiş zamanı noktalı ondalık veya bilimsel gösterim kabul eder (ör. `20.5`, `2e1`).
  Boş, geçersiz, sonlu olmayan, pozitif olmayan zaman ve tahmini 1.000.000 örnek
  sınırını aşan ayarlar durum alanında hata gösterir.

Slider aralıkları ürün tercihidir; hocanın katsayı üst sınırı olarak yorumlanmaz.
Varsayılan pencere 1440×900, desteklenen minimum 1000×740'tır. Her iki boyutta
dört slider, Case ve Run düğmeleri kaydırma olmadan görünür. Euler kimlik rengi
`#FF1D8D`; Exact `#475569`, RK4 `#2563EB` kullanır.

Tam olarak başlangıçta kurulan üçüncü taraf sürümleri yeniden kurmak için
`requirements-dev.txt` yerine `requirements.lock.txt` kullanın.
Kilit dosyası Python 3.11/macOS ortamında oluşturulmuştur; diğer platformlarda
paket uyumluluğu ayrıca kontrol edilmelidir.

## Modüller

| Klasör | Sorumluluk |
|---|---|
| `src/dss/analytical` | Kişi 1: analitik çözüm ve kök sınıflandırması |
| `src/dss/numerical` | Kişi 2: zaman ızgarası, Euler ve RK4 |
| `src/dss/ui` | Kişi 3: PySide6 arayüzü ve controller |
| `src/dss/visualization` | Kişi 4: grafik, hata metrikleri ve export |

`src/dss/contracts.py` ortak tipleri ve doğrulamaları içerir.
`docs/team/README.md` içinde görev rehberleri bulunur; her rehber tek başına ajana verilebilir.
UI mimarisi, API alan eşlemesi ve M1 test kaydı: [docs/modules/ui.md](docs/modules/ui.md).

## Geliştirme

Her modülün karşılık gelen test klasörü ayrılmıştır. Tam headless test paketi:

```powershell
$env:QT_QPA_PLATFORM = "offscreen"
.\.venv\Scripts\python.exe -m pytest -q
Remove-Item Env:QT_QPA_PLATFORM
```

POSIX: `QT_QPA_PLATFORM=offscreen python -m pytest -q`.
Testler UI yaşam döngüsü, girdiler, izole başlangıç, gerçek Run-to-plot akışı,
hata metrikleri, tema geçişi ve dışa aktarmayı kontrol eder.
Test komutu: `python -m pytest -q`. Ortak sözleşme, sınıflandırma ve üç Case için analitik çözüm testleri mevcuttur.
GitHub Actions yapılandırması testler eklenince Kişi 2 tarafından hazırlanacaktır.

Windows yerel UI smoke testi (pencere otomatik açılır ve kapanır):

```powershell
.\.venv\Scripts\python.exe tests/ui/native_smoke.py
```

M4B-2 doğrulama: güncel main **565 passed**, son tam pytest **601 passed**;
yerel Windows smoke **PASS**. Üç Case/yedi yöntem kombinasyonu, gerçek eğri/grid
ve metrikler, dt/2 ve dt/4 yakınsaması, tema renkleri, eski sonuçların reddi,
canvas/worker temizliği ve gerçek PNG/PDF dosyaları doğrulandı. Dört Response
ve iki Error ekran görüntüsü yerel `.venv/ui-m4b2-*.png` dosyalarındadır.
Gerçek dışa aktarmalar `.venv/native-m4b2-{light,dark}-{0,1}.{png,pdf}` altındadır.
Görsel kontrol her iki temada 1440×900 ve 1000×740 boyutlarında yapıldı.

Mevcut bir milyon örnek sınırında tüm veriler korunur. Çözücüler worker içinde;
grafik çizimi ve export GUI üzerinde senkrondur. Üst sınırda iki grafiğin yerel
Agg çizimi toplam 2.18 saniye sürdü; büyük grafik/export kısa etkileşim beklemesi
yaratabilir. Ayrıntılı akış, ölçümler ve M5 öncesi kontrol listesi
[UI belgesinde](docs/modules/ui.md). M5 başlatılmadı; ekip incelemesi bekleniyor.

Commit biçimi: `<type>(<scope>): <description>`.
Geliştirme feature branch ve gözden geçirilmiş PR üzerinden ilerler.
Lab Case'lerini ve matematiksel API'yi görev rehberleri/yönerge ile eşleştirmeden değiştirmeyin.
