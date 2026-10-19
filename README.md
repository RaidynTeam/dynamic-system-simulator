# Dynamic System Simulator

Lab 1 için dört kişinin geliştireceği Python proje iskeleti.

## Durum — M4A real solver orchestration (COMPLETE)

PySide6 arayüzünde varsayılan açık tema ve sağ üstte güneş/ay düğmesiyle anlık
koyu tema geçişi vardır. Seçim QSettings ile sonraki açılışta hatırlanır;
Windows sistem teması arayüzü belirlemez. Solda tek
System Controls kartı, görünür Case düğmeleri, dört slider ve Run Simulation;
sağda temayla eşleşen Matplotlib canvas ve kompakt hata metrikleri boş durumu vardır.
Alt satır hazır/hata/henüz bağlanmamış simülasyon durumunu gösterir.
Ortak veri tipleri, parametre doğrulaması ve üç Case sınıflandırması hazırdır;
analitik üç Case çözümü, ortak zaman ızgarası, Euler ve RK4 API'leri mevcuttur.
`dss.ui.controller.run_simulation(model, config, methods)` tek ızgarada yalnız
seçili çözücüleri istenen sırayla çalıştırır ve gerçek shared Response listesi döndürür.
Girdileri ortak doğrulayıcılara devreder; sayısal hataları değiştirmeden iletir.
Run Simulation düğmesinin hesaplama/grafik bağlantısı M4B'ye bırakılmıştır;
düğme henüz hesaplama yapmaz ve bunu açıkça bildirir. Grafik boştur,
metrik alanı “No results yet” yazar. DEMO veri veya sahte sonuç kullanılmaz.

Sonuç başlığında Response/Error seçimi ve PNG/PDF düğmeleri hazırlanmıştır;
gerçek sonuç yokken kapalıdır. Person 4'ün Figure/metrik/export API'leri hâlâ
boştur. UI bağlantıları yalnız izole test doubles ile doğrulandı; gerçek
visualization entegrasyonu **PARTIAL** durumundadır. M4A controller tamamdır;
M4B Run-to-plot/worker entegrasyonu eklenmedi.
Gelecekte `MainWindow.show_responses()` shared Response nesnelerini doğrular ve
Figure/metrik üretimini Person 4'e bırakır; yazmayı export_figure'a devreder.

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

Örnek akış: Case 2 düğmesine basın, `b0` slider'ını ve bitiş zamanını düzenleyin, yöntemleri
seçin ve Run Simulation'a basın. Hesaplama henüz kullanılamıyor mesajı görünür.

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
Testler pencere açılış/kapanışını, gerekli kontrolleri, Case/alan eşlemesini,
başlangıç adımını, boş seçim mesajını ve eksik modüllerden bağımsız gerçek
uygulama girişini kontrol eder. Gerçek hesaplama doğruluğunu kanıtlamaz.
Test komutu: `python -m pytest -q`. Ortak sözleşme, sınıflandırma ve üç Case için analitik çözüm testleri mevcuttur.
GitHub Actions yapılandırması testler eklenince Kişi 2 tarafından hazırlanacaktır.

Windows yerel UI smoke testi (pencere otomatik açılır ve kapanır):

```powershell
.\.venv\Scripts\python.exe tests/ui/native_smoke.py
```

M4A doğrulama: güncel main başlangıcı **243 passed**, son tam pytest paketi
**317 passed**; iki temada Windows smoke testi **PASS**.
Yeni gerçek controller testleri üç Case, yöntem seçim/sıra aktarımı, ortak ızgara,
parametre/b0 değişiklikleri, adım küçültme, geçersiz girdiler ve taşma aktarımını kapsar.
Tema kalıcılığı, canvas yaşam döngüsü, metrik/grid doğrulaması ve export UI
başarı/hata/iptal akışları test edilir; gerçek visualization API başarısı iddia edilmez.
Görsel olarak kontrol edilen dört görüntü `.venv/ui-m3-{light,dark}-{1440x900,1000x740}.png`
altında yerel olarak tutulur. M4B için Person 4'ün Figure/metrik/export API'leri,
gerçek grafik tema arayüzünde ekip mutabakatı ve kullanıcı onayı gerekir.

Commit biçimi: `<type>(<scope>): <description>`.
Geliştirme feature branch ve gözden geçirilmiş PR üzerinden ilerler.
Lab Case'lerini ve matematiksel API'yi görev rehberleri/yönerge ile eşleştirmeden değiştirmeyin.
