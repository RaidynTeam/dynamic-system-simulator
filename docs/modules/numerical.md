# Sayısal yöntemler ve savunma notları

Bu bölüm, birim basamak girdisine verilen cevabı Euler ve RK4 ile hesaplar.
Ödevin tek bilgi ve gereksinim kaynağı **Lab1 RTS 09102026.doc** dosyasıdır.
Markdown görev rehberi yalnız iş dağılımı için kullanılmıştır.
Buradaki Python yapısı, test toleransları ve deney bitiş zamanları uygulama
tercihleridir; Word'de belirtilen ek zorunluluklar değildir.

## 1. Denklemden koda

Word (1)-(4): `y'' + a1*y' + a0*y = b0*x(t)`.
`a1`, `a0`, `b0` pozitiftir; t>=0 için x(t)=1 ve y(0)=y'(0)=0.
`y` sistemin çıktısıdır. Türev `y'`, bu çıktının o andaki değişim hızıdır.
Örneğin çıktı konum ise türevi hız olur; her sistemin çıktısı konum değildir.

İkinci türevi doğrudan izlemek yerine `v=y'` deriz. Word (12)'de bu değişken
`z` adındadır. Böylece iki birinci dereceden denklem elde edilir:

```text
y' = v
v' = b0 - a1*v - a0*y
```

Kodda `state[i] = [y_i, v_i]`. `_common.derivative` bu iki türevi döndürür.
Euler ve RK4 aynı denklemi kullanır; yalnız bir sonraki değeri tahmin etme
biçimleri farklıdır. Girdi birim basamak olduğu için sağ tarafta b0 bulunur.
Word'ün genel RK4 anlatımındaki x değişkeni, ilk denklemdeki giriş x(t) ile
karıştırılmamalıdır; kodda y/v isimlerini tutarlı kullanıyoruz.

## 2. Zaman adımı

Bilgisayar cevabı sürekli zamanın her noktasında değil, seçtiğimiz zamanlarda
hesaplar. `h`, ardışık iki örnek arasındaki süredir. Küçük h genellikle daha
iyi yaklaşım ve daha fazla hesap demektir.

Word görev 5: `h = 0.1 * 2*pi / sqrt(a0)` başlangıç değeridir.
`make_time_grid` bu değeri kendiliğinden seçmez; verilen `config.dt` ile çalışır.
Arayüz başlangıç değerini seçer, deney betiği de bu formülü açıkça uygular.

Örneğin bitiş 1, adım 0.3 ise sonuç `[0, .3, .6, .9, 1]` olur.
Son aralık 0.1'dir; bu yüzden her döngüde `h = t[i+1] - t[i]` hesaplanır.
Bitiş anına örnek koymak bizim uygulama tercihimizdir. Çözücüler verilen
ızgarayı değiştirmez. Bir milyon örnek sınırı bellek kullanımını sınırlayan
teknik tercihtir. Çok küçük bir adım aşırı örnek gerektiriyorsa açık hata verilir.
Son noktadaki birkaç kayan nokta yuvarlama basamağı, fazladan örnek üretmez.

## 3. Euler ve elle hesap

Word (15), mevcut eğimi adım boyunca sabit kabul eder:

```text
y_new = y + h*v
v_new = v + h*(b0 - a1*v - a0*y)
```

İki satırın sağ tarafı da **eski** y ve v değerlerini kullanır.
Kodda tek vektör ataması bunu sağlar:
`state[i+1] = state[i] + h*derivative(model, state[i])`.

`a1=2, a0=1, b0=1, h=.1` için:

| t | y | v | Sonraki adımda kullanılacak v' |
|---:|---:|---:|---:|
| 0 | 0 | 0 | 1 |
| 0.1 | 0 | 0.1 | 0.8 |
| 0.2 | 0.01 | 0.18 | 0.63 |

İlk adımda y'nin sıfır kalması hata değildir: başlangıçtaki v sıfırdır.
Gerçek çıktı ilk aralık içinde artmaya başlar; Euler başlangıç eğimini
kullandığı için bu artışı ilk örnekte yakalayamaz.

## 4. RK4 ve dört eğim

Word (18)-(19), aynı adım içinde dört farklı tahmin yapar. `s=[y,v]` ve
`f(s)=[v,b0-a1*v-a0*y]` yazarsak:

```text
k1 = f(s)
k2 = f(s + h*k1/2)
k3 = f(s + h*k2/2)
k4 = f(s + h*k3)
s_new = s + h*(k1 + 2*k2 + 2*k3 + k4)/6
```

Word'deki Delta terimleri **artım**, kodda k değerleri **eğimdir**:
`Delta = h*k`. Bu yüzden h bir kez çarpılır. Her k hem y hem v bileşenini
içerir; ara noktada yalnız bir bileşeni değiştirmek RK4 olmaz.

Yukarıdaki Euler örneğinin ilk adımında:
`k1=(0,1)`, `k2=(.05,.9)`, `k3=(.045,.9075)`, `k4=(.09075,.814)`.
Sonuç `y=.00467916666667`, `v=.0904833333333` olur.
Bu sayılar bağımsız elle hesap testi olarak kodda bulunur.

Euler adım başına bir, RK4 dört türev hesabı yapar. Aynı h için RK4 bu
örneklerde daha doğru sonuç verir; tek bir adımı daha pahalıdır.

## 5. Ortak arayüz ve hata davranışı

```python
from math import pi, sqrt
from dss.contracts import ModelParams, SimulationConfig
from dss.numerical import make_time_grid, solve_euler, solve_rk4

model = ModelParams(a1=1., a0=1., b0=1.)
h = .1 * 2*pi / sqrt(model.a0)
t = make_time_grid(SimulationConfig(t0=0., t_end=20., dt=h))
euler = solve_euler(model, t)
rk4 = solve_rk4(model, t)
```

Her sonuç `Response(t, y, v, method)` biçimindedir. Diziler float64'tür;
başlangıçta y=v=0'dır. Response girdilerin kopyasını taşır. Çözücülere verilen
t dizisi sıfırdan başlamalı, sonlu ve kesin artan en az iki örnek içermelidir.
Geçersiz giriş `ValueError`, hesap taşması `FloatingPointError` üretir.
Sonlu fakat kararsız bir sayısal eğri gizlice düzeltilmez.

Mevcut ortak API değiştirilmedi. Sayısal modül Qt veya Matplotlib kullanmaz.
Arayüz sahibi aynı t dizisini analitik, Euler ve RK4'e vererek sonuçları
grafik sahibinin fonksiyonlarına aktarabilir. Controller ve grafik modülünü
bu çalışma içinde uygulamıyoruz.

## 6. Gerçek deney sonuçları

Tam tablolar ve ortam bilgisi [deney kaydında](../evidence/numerical-experiments.md).
Yeniden üretmek için `python tests/numerical/experiments.py` çalıştırılır.
Bu betik dosya değiştirmez; tabloyu standart çıktıya yazar.

### Word görev 5-7 karşılaştırması

Word'ün örnekleri `(a1,a0)=(1,1),(2,1),(3,1)` kullanıldı. `b0=1`, bitiş 20
ve iki yöntem için `max(abs(y_numeric-y_exact))<=.01` bizim deney seçimimizdir.
Bu eşik b0=a0=1 olan bu örnekler içindir; her model için evrensel eşik değildir.
Analitik referans, aynı t dizisinde ortak analitik modülden alınır. Sayısal
testlerde ayrıca Word (8)-(10)'un doğrudan formülleri bağımsız referanstır.

| Case | İlk h | İlk Euler hatası | İlk RK4 hatası | Hedefe ulaşan h | Yarılamalar |
|---|---:|---:|---:|---:|---:|
| 1 | .62831853 | .42456625 | .00119401 | .01963495 | 5 |
| 2 | .62831853 | .13645130 | .00287905 | .03926991 | 4 |
| 3 | .62831853 | .11290948 | .01335000 | .07853982 | 3 |

İlk adımın yönergede verilmiş olması onun yeterince doğru olduğu anlamına
gelmez. Case 3'te RK4 de başlangıçta seçtiğimiz eşiği aşmıştır.
Yarılamalar ayrı tam simülasyonlardır; çözücü içinde uyarlamalı adım yoktur.
Hatalar örnek noktalarında ölçülür; sürekli zamanın tüm noktaları için bir
üst sınır kanıtı değildir. Grafik arkadaşımız bu sonuçları görsel olarak da
karşılaştırmalıdır; bu tablo çalışan arayüz ekran görüntüsünün yerine geçmez.

### Ek yakınsama deneyi

Word (9)'dan `a1=2,a0=b0=1` için `y(t)=1-(1+t)*exp(-t)` kullanıldı.
Seçtiğimiz bitiş t=2; hata yalnız son noktadaki y hatasıdır.

| h | Euler hatası | RK4 hatası |
|---:|---:|---:|
| .1 | 1.4258851585e-2 | 5.1085177122e-7 |
| .05 | 6.9417845866e-3 | 3.0008312391e-8 |
| .025 | 3.4263922472e-3 | 1.8180400518e-9 |

Euler hata oranları 2.054 ve 2.026; RK4 oranları 17.024 ve 16.506 bulundu.
Euler'in global hatası O(h), RK4'ün O(h^4) olduğundan beklenen limitler 2 ve
16'dır. Yeterince küçük adım ve düzgün çözüm varsayımı gerekir; yuvarlama
hatasının baskın olduğu çok küçük adımlarda bu oranlar beklenmez.
Test aralıkları bu deney için Euler'de 1.8-2.3, RK4'te 14-19 seçildi.

Görev rehberindeki t=1 ölçümü kullanılmadı: bu özel modelde analitik y eksi
Euler y farkı `exp(-t)*t*(1-t)*h/2 + O(h^2)` olduğundan t=1'de ilk terim sıfırlanır.
Burada yaklaşık 4 oranı görmek Euler'in genel olarak ikinci dereceden olduğu
anlamına gelmez. t=2 seçimi seninle kararlaştırılan ek test tercihidir.

## 7. Savunma için temel ayrımlar

- **Yerel hata:** Bir adımın, doğru başlangıçtan atıldığında yaptığı hata.
  Adım sonucundaki yerel hata Euler'de O(h^2), RK4'te O(h^5)'tir.
- **Global hata:** Sabit bir zaman aralığında adımların birikmesiyle oluşan
  hata; Euler'de O(h), RK4'te O(h^4).
- **Fiziksel ve sayısal kararlılık:** Pozitif lab katsayıları kararlı fiziksel
  sistem verir. Euler'in `u'=lambda*u` modeli için büyütme çarpanı
  `1+h*lambda` olduğundan `abs(1+h*lambda)<1` gerekir. Büyük h bunu bozabilir.
  Kritik örnekte lambda=-1 ve 0<h<2 gerekir; h=3 ile büyüyen sayısal çıktı
  görmek fiziksel sistemin kararsız olduğu anlamına gelmez.
- **Aynı zaman dizisi:** Karşılaştırılan y değerleri aynı ana ait olmalıdır.
  Farklı zamanlardaki değerleri çıkarmak yöntem hatasını ölçmez.

Kendi sözlerinle yanıtla: İlk Euler adımında y neden sıfır? Güncellenmiş y'yi
v hesabında kullanırsak ne değişir? RK4'te h neden iki kez çarpılmaz?
Adımı yarıya indirince süre ve doğruluk nasıl değişir? Son aralık neden kısa?
Test başarısı, bu soruları açıklayabildiğini tek başına kanıtlamaz.

## 8. Windows kurulumu ve durum

Depo kökünde PowerShell komutları:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe tests/numerical/experiments.py
```

Python 3.11 veya üstü gerekir. Yerel doğrulama Windows/Python 3.14.5 ile
yapılmıştır; CI Windows/Python 3.11 için yapılandırılmıştır. Mevcut paket
ayarları yeniden yazılmadı; editable kurulum ve depo dışından import doğrulandı.
macOS kaynaklı mevcut kilit dosyasının Windows'ta doğrulandığı iddia edilmez.
Yerel bağımlılık sürümleri `docs/evidence/numerical-environment.txt` içindedir.

- Dal: `feat/numerical-methods`; başlangıç main `c968ff6`;
  ekip güncellemeleri main `1d26c8c` dahil birleştirildi.
- Izgara commit'i: `1ea380d`; çözücüler ve testler: `6616fcd`.
- Sayısal bölüm: 58 test geçti; mevcut ekip testleri ilk kontrolde 157 geçti.
- Güncel ekip koduyla tam test: 220 geçti (162 mevcut + 58 sayısal). Kayıt:
  `docs/evidence/numerical-tests.txt`.
- Sayısal kod PR #10 ile main'e alındı. Main `2b51883` için Windows/Python 3.11
  [CI çalışması başarılı](https://github.com/RaidynTeam/dynamic-system-simulator/actions/runs/39309145462).
  Bu, yukarıdaki yerel Python 3.14 test kaydından ayrı doğrulanmış sonuçtur.
- Kalan ekip işi: gerçek controller/grafik entegrasyonu, 5-6 çalışan uygulama
  ekran görüntüsü, ortak rapor ve teslim paketi. Sayısal API kullanıma hazırdır.
- Öğrenme: temel açıklama ve alıştırmalar hazır; öğrencinin sözlü açıklama
  yeterliliği henüz değerlendirilmedi; Türkçe anlatım kullanıcı isteğiyle ertelendi.

## 9. M5 rapor katkısı ve teslim

- [İngilizce rapor bölümü](../report/numerical-report.md) hazır: görev,
  algoritmalar, API, ölçülen deney tabloları, kararlılık ve sonuç.
- [Teslim kaydı ve altı ekran görüntüsü senaryosu](numerical-handoff.md) hazır.
- M5 belge dalı: `docs/numerical-m5`; taban main `bf033de`.
- M1-M4 teknik işleri tamam. M5'in rapor katkısı hazır; Kişi 4'ün PR incelemesi
  beklemede. Kontrol anında grafik modülleri boş ve ilgili PR henüz yok.
- Sıradaki ekip işi: gerçek grafik/controller entegrasyonu ve ekran görüntüleri.
  Başka kişilerin modülleri bu teslimde değiştirilmedi.
