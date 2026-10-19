# Analitik modül — M1, M2 ve M3

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
Tolerans bandı dışında işaret korunur. Kök değerleri hesaplanmaz; M3 itibarıyla üç Case için y(t) ve v(t) hesaplanır.

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
M2 aşamasında Case 1/3 desteklenmiyordu; M3 artık üç Case’i de destekler.

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

## M3 — Case 1 ve Case 3

### Case 1: karmaşık eşlenik kökler — PDF (8)

`omega=sqrt(a0-sigma²)`, `K=b0/a0`:

`y=K*[1-exp(-sigma*t)*(cos(omega*t)+sigma/omega*sin(omega*t))]`

`v=b0/omega*exp(-sigma*t)*sin(omega*t)`

Başlangıç koşullarından sabit özel çözüm K, homojen çözüm katsayıları
`C1=-K`, `C2=-K*sigma/omega` elde edilir. Türev alındığında cos terimleri
birbirini götürür ve yukarıdaki v kalır. Salınım ve son değeri aşma beklenir;
bu fiziksel davranış hata olarak bastırılmaz.

Kritik sınıra yakın omega küçükken sin(omega*t)/omega yerine
`t*sinc(omega*t/pi)` kullanılır (NumPy sinc tanımı sin(pi*x)/(pi*x)).
`1-cos(angle)` yerine `2*sin(angle/2)²` ve `1-exp(-x)` yerine `-expm1(-x)`
kullanılarak yakın sayıların çıkarılmasındaki kayıp azaltılır.

### Case 3: ayrık gerçek kökler — PDF (10)

`delta=sqrt(sigma²-a0)`, `s1=-sigma+delta`, `s2=-sigma-delta`:

`y=K*[1+s2/(s1-s2)*exp(s1*t)+s1/(s2-s1)*exp(s2*t)]`

`v=b0/(s1-s2)*[exp(s1*t)-exp(s2*t)]`

Katsayılar y(0)=v(0)=0 koşullarından gelir. Üretim kodunda yavaş kök
`s1=-a0/(sigma+delta)` ile bulunur; bu iki yakın sayıyı çıkarma ihtiyacını kaldırır.
`gap=2*delta`, `E=-expm1(-gap*t)/gap` kullanılarak
`y=K*[-expm1(s1*t)+s1*exp(s1*t)*E]`, `v=b0*exp(s1*t)*E`
hesaplanır. İki gerçek üstel de büyümez; exp*cosh biçiminin ara taşması önlenir.

### Ortak erken zaman koruması

`max(a1,sqrt(a0))*t < 0.01` iken y, diferansiyel denklemden türetilen
12. derece kuvvet serisiyle değerlendirilir. `y=sum(c_n*t^n)` için
`c0=c1=0`, `c2=b0/2` ve
`c_n=-(a1*(n-1)*c_(n-1)+a0*c_(n-2))/(n*(n-1))`.
Kod önce `b0*t²` çarpanını ayırıp boyutsuz küçük terimlerle çalışır;
v aynı serinin türevidir. Böylece üç Case için de t=1e-12 gibi örneklerde
başlangıç cevabı sıfıra yuvarlanmaz. M2’nin özel erken-zaman serisi bu ortak
korumayla değiştirilmiştir.

Kritik sınıflandırma toleransı ve API v0.2 aynıdır. Aşırı girdilerde
float64 ara taşması açık FloatingPointError verir; sınırsız aralık iddia edilmez.

## Durum kaydı

- Sözleşme: v0.2, imza aynı: `solve_analytical(model,t) -> Response`.
- M1 PR #1 ve M2 PR #3 main’e merge edildi.
- Branch: feat/analytical-m3; başlangıç main commit’i bb9a9d7.
- M3 yerel uygulama ve testleri tamam; push/PR/review/merge yapılmadı.
- Test: `QT_QPA_PLATFORM=offscreen MPLBACKEND=Agg .venv/bin/python -m pytest -q`
  → 122 passed; analitik, ortak sözleşme, UI ve entegrasyon testleri birlikte geçti.
- Kanıt: `docs/evidence/analytical-m3-tests.txt`.
- Yeni testler: üç Case için 80 basamaklı Decimal referansı; kritik sınıra iki yandan
  yaklaşım; küçük zamanlar; ayrık köklerde geniş ölçek; farklı doğal frekanslar;
  son değer, b0 ölçekleme, monotonluk/salınım; y/v türev tutarlılığı ve ODE artığı.
- M2’deki artık geçersiz “Case 1/3 desteklenmiyor” testleri kaldırıldı.
- Numerical ekibinden blokaj yok. Sıradaki görev M4: numerical modülü hazır
  olduğunda aynı ızgarada Euler/RK4 karşılaştırması ve deney/rapor kanıtı.
- Arayüzün hesaplama katmanına bağlanması Kişi 3’e; grafik üretimi Kişi 4’e aittir.
