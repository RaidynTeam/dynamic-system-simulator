# Analitik modül — M1

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
Tolerans bandı dışında işaret korunur. Henüz kök değerleri veya y(t) hesaplanmaz.

Durum denklemi: `y'=v`, `v'=b0-a1*v-a0*y` ve y(0)=v(0)=0.
Numerical modülü aynı modeli kullanacaktır.

## Kullanım

```python
from dss.contracts import ModelParams
from dss.analytical import classify_case

model = ModelParams(a1=1, a0=1, b0=1)
assert classify_case(model) == 1
```

## Durum kaydı

- Sözleşme: v0.2; üç parametreli sıfır başlangıçlı birim basamak modeli.
- Branch: feat/analytical-m1.
- M1 yerel uygulama ve testleri tamamlandı; PR/review/merge henüz yapılmadı.
- Test: `.venv/bin/python -m pytest -q` → 70 passed.
- Kanıt: `docs/evidence/analytical-m1-tests.txt`.
- Bu ortamda editable kurulumun .pth kaydı yeni süreçlerde src yolunu eklemiyordu.
  Testlerin kurulum durumundan bağımsız çalışması için pytest pythonpath=["src"] ayarı eklendi.
- Sıradaki görev: M2, PDF (9) kritik sönüm y(t), v(t) ve bağımsız doğruluk testleri.
- M1 blokajı yok. Diğer modüllerden beklenen bitmiş API yok.
- Analitik çözücü, Euler/RK4, arayüz ve grafikler bu aşamada uygulanmadı.
