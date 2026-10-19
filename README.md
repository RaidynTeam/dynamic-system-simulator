# Dynamic System Simulator

Lab 1 için dört kişinin geliştireceği Python proje iskeleti.

## Durum — M1 UI skeleton

PySide6 masaüstü arayüzü çalışır: parametreler, Case seçimi, Exact / Euler / RK4
seçimleri, Run Simulation, Matplotlib canvas, hata metrikleri ve durum alanı.
Ortak veri tipleri, parametre doğrulaması ve üç Case sınıflandırması hazırdır;
M3 branch’inde üç Case için analitik çözücü hazırdır. Euler/RK4 ve grafik fonksiyonları henüz uygulanmadı; arayüzün hesaplama bağlantısı ayrı aşamadır.
Run Simulation hesaplama yapmaz; M1 durum mesajı gösterir. Grafik boştur,
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

Örnek M1 akışı: Case 2 seçin, `b0` ve bitiş zamanını düzenleyin, yöntemleri
seçin ve Run Simulation'a basın. Hesaplama henüz kullanılamıyor mesajı görünür.
`a0` değişince veya Case seçilince `dt` ilk lab değerine döner; daha sonra
elle azaltılabilir. “Reset Δt” düğmesi aynı formülü tekrar uygular.

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

Her modülün karşılık gelen test klasörü ayrılmıştır. M1 headless testleri:

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

Commit biçimi: `<type>(<scope>): <description>`.
Geliştirme feature branch ve gözden geçirilmiş PR üzerinden ilerler.
Lab Case'lerini ve matematiksel API'yi görev rehberleri/yönerge ile eşleştirmeden değiştirmeyin.
