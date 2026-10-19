# Analitik modül — M1 ve M2

## Ne yapıldı ve neden?

`ModelParams(a1,a0,b0)` üç pozitif lab parametresini taşır. Frozen dataclass alanların
sonradan yanlışlıkla değiştirilmesini engeller. Parametreler yapıcıda kontrol edilir;
`ValueError` arayüz katmanında kullanıcı mesajına çevrilebilir.

`SimulationConfig(t0,t_end,dt)` zaman ayarlarını taşır. Labda t0=0 sabittir.
`Response(t,y,v,method)` çözücüler ile grafik modülü arasındaki ortak biçimdir.
NumPy dizileri float64 olmalı, aynı uzunlukta olmalı, zaman sıfırdan başlayıp artmalıdır.
Response giriş dizilerini kopyalar; frozen olması NumPy dizi içeriğini salt okunur yapmaz.
`ErrorMetrics(max_abs,rmse)` metriklerin taşıyıcısıdır; hesaplaması Kişi 4'e aittir.

## Matematik ve sınıflandırma

PDF (5): `s²+a1*s+a0=0`. `D=a1²-4*a0` işareti kök türünü belirler.
D negatifse Case 1 (karmaşık), sıfırsa Case 2 (tekrarlı), pozitifse Case 3 (ayrık gerçek).
Pozitif katsayılarla gerçek kısımlar negatiftir; bu lab sistemleri kararlıdır.
`b0` genliği değiştirir, kök sınıfını değiştirmez.

`classify_roots` eski kök etiketlerini korur; `classify_case` PDF'nin 1/2/3 numarasını döndürür.
Doğrudan a1² hesaplamak büyük değerlerde taşabileceğinden, sınıflandırma
`q=(a1/s)²-(2*sqrt(a0)/s)²`, `s=max(a1,2*sqrt(a0))` ile yapılır.
`abs(q)<=64*float64_epsilon` kritik kabul edilir. Bu sayıların büyüklüğüne göre
ölçeklenmiş bir yuvarlama toleransıdır; kesin sembolik eşitlik değildir.
Tolerans bandı dışında işaret korunur. Kök değerleri hesaplanmaz; M2’de Case 2 için y(t) ve v(t) hesaplanır.

Durum denklemi: `y'=v`, `v'=b0-a1*v-a0*y` ve y(0)=v(0)=0.
Numerical modülü aynı modeli kullanacaktır.

## Kullanım

```python
from dss.contracts import ModelParams
from dss.analytical import classify_case

model = ModelParams(a1=1, a0=1, b0=1)
assert classify_case(model) == 1
```

## M2 — Kritik sönüm çözümü

PDF (9) için `sigma=a1/2`, `K=b0/a0`:

`y(t)=K*[1-(1+sigma*t)*exp(-sigma*t)]`

Türev alındığında:

`v(t)=K*sigma²*t*exp(-sigma*t)`

Bu formül nasıl elde edilir? Sabit özel çözüm K'dır. Tekrarlı kökte homojen
çözüm `(C1+C2*t)*exp(-sigma*t)` olur. y(0)=0 koşulu C1=-K, v(0)=0 koşulu
C2=-K*sigma verir. Bunları birleştirince PDF'nin (9) formülü çıkar.

### Kullanım

```python
import numpy as np
from dss.contracts import ModelParams
from dss.analytical import solve_analytical

response = solve_analytical(
    ModelParams(a1=2, a0=1, b0=1),
    np.array([0., 0.1, 0.5, 1., 5.]),
)
```

Girdi ızgarası float64, sonlu, tek boyutlu, sıfırdan başlayan ve kesin artan
en az iki örnek olmalıdır. Çözücü ızgarayı üretmez; numerical modülüne ihtiyaç duymaz.
Sonuç aynı ızgarada y/v ve `method="analytical"` taşır, girdi değiştirilmez.
Case 1/3 şu anda desteklenmediği için `NotImplementedError` verir.

### Küçük zamanlarda hassasiyet

Doğrudan `1-(1+x)*exp(-x)` ifadesi x çok küçükken birbirine çok yakın
sayıları çıkarır ve küçük pozitif cevabı sıfır yapabilir. x=sigma*t için
`-expm1(-x)-x*exp(-x)` kullanılır; x<0.001 bölgesinde ise
`x²/2-x³/3+x⁴/8-x⁵/30+x⁶/144-x⁷/840+x⁸/5760` serisi değerlendirilir.
Bu dal hem sıfır başlangıcını hem t=1e-12 gibi küçük örnekleri korur.
Hız hesabı sigma² yerine `K*sigma*x*exp(-x)` olarak düzenlenir.
Sayısal taşma/geçersiz hesap `FloatingPointError` olur; üstel sönümün sıfıra
underflow etmesi normal kabul edilir. Aşırı katsayılarda ara hesaplar float64
aralığını aşarsa sonuç yerine açık hata verilir.

Kritik sınıflandırmanın tolerans bandındaki modeller aynı tekrarlı kök
formülünü kullanır; sınırdaki bu davranış yakın kritik model yaklaşımıdır.

## Durum kaydı

- Sözleşme: v0.2; M2 ortak API imzasını değiştirmez.
- M1 branch/commit: feat/analytical-m1 / c7d05f9.
- M1 push ve PR tamam: https://github.com/RaidynTeam/dynamic-system-simulator/pull/1
- M1 PR #1 kullanıcı tarafından merge edildi; origin/main üzerinden doğrulandı.
- M2 branch: feat/analytical-m2; M1 merge sonrası güncel origin/main üzerine rebase edildi.
- M2 uygulama/testleri tamam; güncel main üzerine yalnız M2 değişiklikleriyle incelemeye hazır.
- Test: `.venv/bin/python -m pytest -q` → 91 passed (70 M1 + 21 M2).
- Kanıt: `docs/evidence/analytical-m2-tests.txt`.
- M2 testleri bağımsız yüksek hassasiyetli Decimal referansı, başlangıç koşulları,
  limit, monotonluk, model denklemi, b0 ölçekleme, küçük zaman, düzensiz ızgara,
  veri sahipliği, geçersiz giriş ve desteklenmeyen Case'leri kapsar.
- Ortamda editable .pth kaydı src yolunu eklemiyordu; M1'de pytest
  pythonpath=["src"] ayarı ile testler kurulum durumundan bağımsız hale getirildi.
- Sıradaki görev: M3, PDF (8) ve (10) ile Case 1/3 ve kritik sınıra yakın doğruluk.
- Numerical modülünden yanıt/bitmiş API beklenmiyor; ortak API v0.2 korunuyor.
