# Dynamic System Simulator

Lab 1 için dört kişinin geliştireceği Python proje iskeleti.

## Durum — M2 slider controls

PySide6 masaüstü arayüzü çalışır: parametreler, Case seçimi, Exact / Euler / RK4
seçimleri, Run Simulation, Matplotlib canvas, hata metrikleri ve durum alanı.
Ortak veri tipleri, parametre doğrulaması ve üç Case sınıflandırması hazırdır;
analitik Case 2 çözümü main'de mevcuttur; Case 1/3, sayısal çözücüler ve grafik
fonksiyonları için diğer üyelerin çalışmaları devam eder.
Run Simulation hesaplama yapmaz; UI durum mesajı gösterir. Grafik boştur,
hata hücreleri “Not calculated” yazar. DEMO veri veya sahte sonuç kullanılmaz.

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

Aktif Python ortamında diğer platformlarda `python -m dss` kullanın.

Örnek M2 akışı: Case 2 seçin, `b0` slider'ını ve bitiş zamanını düzenleyin, yöntemleri
seçin ve Run Simulation'a basın. Hesaplama henüz kullanılamıyor mesajı görünür.

- `a1`, `a0`, `b0`: QSlider, 0.01–20.00 aralığı, 0.01 adım ve sayısal değer etiketi.
- `dt`: logaritmik QSlider, 0.000001–10 saniye, her onluk mertebede 200 adım.
- Auto dt başlangıçta açıktır; `a0` değişince ilk lab formülü uygulanır.
  `dt` slider'ını elle değiştirmek veya `dt / 2`, `dt × 2` kullanmak Auto dt'yi kapatır.
- Case seçimi ve “Reset Δt” Auto dt'yi açar ve formülü uygular; `b0` korunur.
- Auto dt ve yarılama/ikiye katlama tam kayan nokta değerini korur; slider kolu
  en yakın logaritmik konumu gösterir. Hesaplamaya aktarılacak değer etikette gösterilir.
- Aralık dışı değerler önceki değeri korur ve hata mesajı verir; sessiz kırpma yapılmaz.
- Başlangıç ve bitiş zamanı ayrı alanlardır; başlangıç API v0.2 gereği sıfırda sabittir.
  Bitiş zamanı noktalı ondalık veya bilimsel gösterim kabul eder (ör. `20.5`, `2e1`).
  Boş, geçersiz, sonlu olmayan, pozitif olmayan zaman ve tahmini 1.000.000 örnek
  sınırını aşan ayarlar durum alanında hata gösterir.

Slider aralıkları ürün tercihidir; hocanın katsayı üst sınırı olarak yorumlanmaz.
Küçük pencerelerde sol panel kaydırılır; Run Simulation görünür kalır.

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

M2 doğrulama: tam pytest paketi **137 passed**; Windows smoke testi **PASS**.
Smoke görüntüleri `.venv/ui-m2-native*.png` altında yerel olarak tutulur.
M3 ve gerçek hesaplama entegrasyonu bu aşamaya dahil değildir.

Commit biçimi: `<type>(<scope>): <description>`.
Geliştirme feature branch ve gözden geçirilmiş PR üzerinden ilerler.
Lab Case'lerini ve matematiksel API'yi görev rehberleri/yönerge ile eşleştirmeden değiştirmeyin.
