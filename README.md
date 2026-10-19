# Dynamic System Simulator

Lab 1 için dört kişinin geliştireceği Python proje iskeleti.

## Durum

M1: ortak veri yapıları, parametre doğrulaması ve üç Case sınıflandırması hazırdır.
M2: Case 2 kritik sönüm analitik y(t) ve v(t) çözümü hazırdır. Case 1/3, Euler, RK4, arayüz ve grafik fonksiyonları henüz uygulanmadı.
Çözücü ve arayüz dosyaları sonraki aşamalar için boştur; şu anda çalışan bir GUI yoktur.
Lab modeli ve teslim koşulları `docs/lab-requirements.md` içinde kaynak PDF ile eşleştirilmiştir. Ortak API v0.2: `ModelParams(a1,a0,b0)`.

## Kurulum

Python 3.11 veya üzeri kullanın. Bu klasörde hazırlanan `.venv` yerel ortamdır ve Git'e eklenmez.

```sh
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt
python -m pip install -e .
```

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

## Geliştirme

Test komutu: `python -m pytest -q`. M1 sözleşme/sınıflandırma ve M2 kritik sönüm testleri mevcuttur.
GitHub Actions yapılandırması testler eklenince Kişi 2 tarafından hazırlanacaktır.

Commit biçimi: `<type>(<scope>): <description>`.
Geliştirme feature branch ve gözden geçirilmiş PR üzerinden ilerler.
Lab Case'lerini ve matematiksel API'yi görev rehberleri/yönerge ile eşleştirmeden değiştirmeyin.
