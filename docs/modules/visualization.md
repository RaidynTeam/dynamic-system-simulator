# Görselleştirme — Kişi 4, M2

## Güncel milestone: M2 — yanıt karşılaştırması

Durum: **M2 için TAMAMLANDI**. `build_response_figure` seçili yöntemlerin y(t)
eğrilerini tek figürde, ortak zaman ekseninde çiziyor. `compute_error`,
`build_error_figure` (M3) ve `export_figure` (M4) hâlâ yazılmadı; bu yüzden
Kişi 3'ün `load_visualization_api()` çağrısı artık eksik olarak
`build_error_figure`'ı bildiriyor — M1'de `build_response_figure` diyordu.
İlerleme dürüstçe görünüyor.

Ortak API v0.2 bozulmadı. Başka kişiye ait dosya değiştirilmedi.

### İmza ve sözleşme uyumu

```python
build_response_figure(responses, *, theme="light", title=None) -> Figure
```

Sözleşmedeki `build_response_figure(responses: list[Response]) -> Figure`
çağrısı aynen çalışır. Eklenen iki parametre **sadece anahtar kelimeli ve
varsayılanlı**; sözleşme bozulmuyor, genişliyor.

- `theme`: Kişi 3'ün M4B-2'de koyu/açık temayı geçirebilmesi için. M1'de
  önerilmişti, Kişi 3 M4B-1 belgesinde nihai anlaşmayı M4B-2'ye bıraktı.
- `title`: varsayılan başlık `"Unit step response comparison"`. Sözleşme imzası
  `ModelParams` almadığı için figür a1/a0/b0 değerlerini kendisi bilemez;
  isteyen çağıran zengin bir başlık geçebilir (ör. `"Case 1  a1=1  a0=1  b0=1"`).
  Rapor ekran görüntülerinde bu işe yarayacak.

### Çizim kuralları

- **Yalnız y(t) çizilir.** v (hız) bu figürde yok; hata eğrileri M3'te.
- **Legend sırası sabittir:** Exact, Euler, RK4 — kullanıcı yöntemleri hangi
  sırayla seçerse seçsin. Görsel üst üste binme sırasını `zorder` belirler,
  çizim sırası değil. Böylece ardışık çalıştırmalarda legend yer değiştirmez.
- **Eksen etiketleri:** `Time (s)` ve `Output y(t)`. y için **birim yazılmaz** —
  yönerge y'nin neyi ölçtüğünü hiç söylemiyor, uydurma birim desteklenmeyen bir
  iddia olurdu. Bu bir testle sabitlenmiştir.
- **Zaman ekseni** ilk örnekte başlar; Matplotlib'in varsayılan %5 boşluğu
  t=0'da gereksiz boşluk bırakıyordu.
- **İşaretçi seyreltme:** en çok `MAX_MARKERS = 40` işaretçi. dt küçüldükçe
  örnek sayısı on binlere çıkıyor; her örneğe işaretçi koymak eğriyi tamamen
  kapatıyordu. Adım `ceil(N / 40)` olarak hesaplanır, Exact zaten işaretçisiz.

### Reddedilen girdiler

Sessiz düzeltme yok, hepsi `ValueError`:

| Girdi | Neden |
|---|---|
| Boş liste / tuple | Çizilecek bir şey yok |
| `Response` olmayan öğe, liste olmayan girdi, tek `Response` | Ortak sözleşme dışı |
| Aynı yöntem iki kez | Legend belirsizleşir |
| Farklı zaman ızgaraları | **Örtük interpolasyon yapılmaz**, açık hata verilir |
| Bozulmuş `Response` | Ortak `validate_response` yakalar |
| Boş/metin olmayan `title`, bilinmeyen `theme` | Anlamsız çıktı üretmek yerine hata |

### Çalıştırılan testler ve gerçek sonuçlar

Python 3.11.9, Windows 11. Taban: güncel main `e71e723` (Kişi 3'ün M4B-1'i dahil).

```
QT_QPA_PLATFORM=offscreen MPLBACKEND=Agg python -m pytest -q
445 passed

MPLBACKEND=Agg python -m pytest tests/visualization/test_plots.py -q
43 passed
```

445 = güncel main tabanı 402 + bu dalın 43 testi. Mevcut hiçbir test
değiştirilmedi. Testler üç Case'in gerçek `solve_analytical` / `solve_euler` /
`solve_rk4` çıktısını kullanıyor; çizilen x/y verisinin girdiyle birebir aynı
olduğu, girdinin değiştirilmediği, çağıranın listesinin yeniden sıralanmadığı ve
ardışık çağrıların önceki figüre çizgi eklemediği doğrulanıyor.

**Görsel kontrol yapıldı.** Dört figür gerçek çözücü çıktısıyla üretilip
incelendi: Case 1 ve Case 3, `dt = 0.1*2π/√a0 = 0.6283 s` (N=33), açık ve koyu
tema; ayrıca Case 1 için `dt = h0/32 = 0.0196 s` (N=1020). Case 1'de Euler'in
aşımı ve salınımı, Case 3'te aşımsız monoton yükseliş beklendiği gibi görünüyor;
küçük adımda üç eğri çakışıyor. İşaretçi seyreltme 1020 örnekte doğru çalıştı.
Bu görüntüler depoya eklenmedi — rapora girecek ekran görüntüleri gerçek
uygulamadan, Kişi 3'ün M4B-2 entegrasyonundan sonra alınacak.

### M2'nin bilinen eksikleri

- `metrics.py` ve `export.py` hâlâ boş (M3/M4).
- Koyu tema eğri renkleri hâlâ Kişi 3'ün onayını bekliyor; `theme="dark"`
  çalışıyor fakat nihai anlaşma M4B-2'de.
- Figür `ModelParams` almadığı için başlıkta a1/a0/b0 ancak çağıran geçerse
  görünür. Kişi 3'e M4B-2'de `title` geçmesi önerilir.

## Geçmiş kayıt: M1 — bağımsız grafik altyapısı

Durum: **M1 için TAMAMLANDI**. Qt'den ve `pyplot`'tan bağımsız Figure üretimi,
ortak yöntem kimliği (renk + çizgi deseni), iki tema ve sözleşmedeki örnek veri
hazırdır. `build_response_figure`, `build_error_figure`, `compute_error` ve
`export_figure` sırasıyla M2, M3 ve M4'e aittir ve **bilerek yazılmamıştır**;
`plots.py`, `metrics.py` ve `export.py` boş bırakılmıştır. Bu nedenle Kişi 3'ün
`load_visualization_api()` çağrısı hâlâ doğru şekilde `VisualizationUnavailable`
veriyor ve arayüz "sonuç yok" durumunu dürüst biçimde gösteriyor.

Ortak API v0.2 değiştirilmemiştir. Başka kişiye ait hiçbir dosya düzenlenmemiştir.

### Bu aşamada eklenen dosyalar

| Dosya | İçerik |
|---|---|
| `src/dss/visualization/styles.py` | Yöntem kimliği ve tema paletleri; saf veri, Matplotlib içe aktarmaz |
| `src/dss/visualization/figures.py` | Qt'siz `Figure` üretimi ve eksen/tema uygulaması |
| `src/dss/visualization/__init__.py` | Yalnız M1'de gerçekten var olan isimleri dışa verir |
| `src/dss/demo_data.py` | `make_demo_responses()` — yalnız geliştirme/test örneği |
| `tests/visualization/` | 57 test: kimlik, tema, figür, izolasyon, örnek veri |

### Genel API (M1'de hazır olan)

```python
new_figure(mode="light", *, size=(7.2, 4.5), dpi=100) -> Figure
style_axes(axes, mode="light") -> None
apply_figure_theme(figure, mode="light") -> Figure
method_style(method, mode="light") -> MethodStyle
method_color(method, mode="light") -> str
plot_kwargs(method, mode="light") -> dict      # Axes.plot(**kwargs) icin hazir
figure_theme(mode="light") -> FigureTheme
METHOD_ORDER, METHOD_LABELS, METHOD_COLORS, METHOD_LINESTYLES, FIGURE_THEMES
```

Kişi 3 için tipik kullanım:

```python
from dss.visualization import new_figure, plot_kwargs, style_axes

figure = new_figure(mode)                  # canvas bagli degil, eksen yok
axes = figure.add_subplot()
for response in responses:
    axes.plot(response.t, response.y, **plot_kwargs(response.method, mode))
axes.legend()
style_axes(axes, mode)                     # legend dahil temayi uygular
canvas = FigureCanvasQTAgg(figure)         # Qt tarafi Kisi 3'te kalir
```

### Neden pyplot kullanılmıyor

`matplotlib.pyplot` figürleri genel (global) bir yöneticide tutar. Bu durumda her
çalıştırma bellekte figür biriktirir, `close()` unutulursa sızıntı olur ve
`pyplot` içe aktarıldığı anda bir arayüz backend'i seçmeye çalışır. Bunun yerine
`matplotlib.figure.Figure` doğrudan kullanılıyor: global kayıt yok, backend
seçimi yok, Qt bağımlılığı yok. `tests/visualization/test_isolation.py` bunu ayrı
bir alt süreçte kanıtlıyor — figür kurulduktan sonra `sys.modules` içinde ne
`matplotlib.pyplot` ne de bir Qt paketi bulunuyor.

Her çağrı yeni bir `Figure` döndürür. Bu, rehberdeki "ardışık çağrılar önceki
Figure'a çizgi eklemez" kabul ölçütünün doğrudan karşılığıdır ve test edilmiştir.

### Yöntem kimliği ve tek kaynak önerisi

Açık temadaki renkler ekibin `docs/modules/ui.md` içinde anlaştığı değerlerdir:
Exact `#475569`, Euler `#FF1D8D`, RK4 `#2563EB`. Legend'da içsel `analytical`
adı değil, yönergenin dili olan **Exact** yazar.

Renk tek ayırt edici kanal değildir. Her yöntemin ayrıca kendi çizgi deseni,
kalınlığı ve işaretçisi vardır:

| Yöntem | Renk (açık) | Çizgi | Kalınlık | İşaretçi |
|---|---|---|---:|---|
| Exact | `#475569` | düz | 3.2 | yok |
| Euler | `#FF1D8D` | uzun kesik | 1.6 | içi boş daire |
| RK4 | `#2563EB` | nokta-kesik | 1.6 | içi boş üçgen |

Referans eğrisi en kalın ve en altta çizilir. Bu bilinçli bir karardır: RK4
çoğu durumda Exact ile neredeyse çakışır, ince bir referans üstteki eğrinin
altında tamamen kaybolur. Kalınlık farkı, üstteki kesik çizginin iki yanında
görünür bir gri hale bırakır. İlk denemede RK4'ün deseni çok sıktı ve Exact'i
kapatıyordu; görsel kontrolden sonra desen seyreltildi ve kalınlık farkı 2.4/1.8
yerine 3.2/1.6 yapıldı.

**Kişi 3'e öneri (tek taraflı değişiklik değildir):** `src/dss/ui/colors.py`
içindeki `METHOD_COLORS` aynı değerlerin ikinci bir kopyasıdır. İkisinin zamanla
ayrışmaması için UI'ın `dss.visualization.styles` içinden içe aktarması
önerilir. `styles.py` bilerek Matplotlib içe aktarmaz, bu yüzden böyle bir
import UI'a ek bağımlılık getirmez. Bağımlılık yönü (`visualization → ui` değil,
`ui → visualization`) sözleşmeye uygundur.

### Koyu tema: ölçülmüş gerekçe

Kişi 3 koyu temada gerçek eğri renklerinin Kişi 4'ün sorumluluğunda olduğunu not
etmişti. Anlaşılan renkler koyu kart `#1E293B` üzerinde ölçüldü:

| Eğri | Koyu kart üzerinde kontrast | Durum |
|---|---:|---|
| Exact `#475569` | 1.93:1 | metin dışı işaretler için 3:1 eşiğinin altında |
| RK4 `#2563EB` | 2.83:1 | eşiğin altında |
| Euler `#FF1D8D` | 3:1 üzeri | yeterli |

Bu yüzden koyu temada yalnız eşiği geçemeyen iki renk açıldı:
Exact `#CBD5E1`, RK4 `#60A5FA`. **Euler `#FF1D8D` iki temada da aynıdır**, çünkü
Kişi 3 özellikle bu kimliğin korunmasını istedi. Değişiklik ayrıca en kötü renk
körlüğü ayrımını ΔE 8.4'ten 16.7'ye çıkarıyor. Ham ölçümler:
[`docs/evidence/visualization-m1-palette.txt`](../evidence/visualization-m1-palette.txt).

Bu bir **öneridir**; koyu tema eğri renkleri Kişi 3 ile mutabakat gerektirir.
Açık tema değerlerine dokunulmamıştır.

### Tema arayüzü

Kişi 3'ün istediği "Qt'den bağımsız tema arayüzü" iki parçadan oluşur:

1. Figür kurulurken `mode` verilir (`new_figure`, `plot_kwargs`, `style_axes`).
   M2'de `build_response_figure(responses, *, theme="light")` biçiminde, **sadece
   anahtar kelimeli ve varsayılanlı** bir parametre önerilecektir; ortak
   sözleşmedeki konumsal çağrı (`build_response_figure(responses)`) bozulmaz.
2. Kullanıcı tema düğmesine bastığında figürü yeniden kurmadan
   `apply_figure_theme(figure, mode)` çağrılır. Bu fonksiyon zemin, eksen, grid,
   tik, başlık ve legend renklerini günceller.

Önemli sınır: `apply_figure_theme` **eğri renklerini değiştirmez.** Bir çizginin
hangi yönteme ait olduğunu Matplotlib nesnesinden güvenle okuyamayız; koyu tema
eğri renkleri istenirse figür yeniden kurulmalıdır. Bu, fonksiyonun docstring'inde
ve testinde açıkça belirtilmiştir.

### Örnek veri ve README çelişkisi

Ortak sözleşme v0.2 `dss.demo_data.make_demo_responses()` istiyor; README ise
"DEMO veri veya sahte sonuç kullanılmaz" diyor. İkisi de korunacak şekilde
çözüldü: fonksiyon sözleşmedeki imzayla yazıldı, fakat **üretim kodu bu modülü
içe aktarmıyor.** Üç gerçek çözücü de main'de hazır olduğundan arayüzün örnek
veriye ihtiyacı yok.

Eğriler kasıtlı olarak yönergenin üç kapalı form çözümünden biri değildir;
`y = t²/(1+t²)` rasyonel doyum eğrisi kullanılır. İki nedeni var: Kişi 1'in
formüllerinin ikinci bir kopyası oluşmasın, ve bu eğriler yanlışlıkla gerçek
sonuç sanılmasın. Yöntemler arası sapmalar (Euler +%6, RK4 −%2.5, zamanla
sönümlenen) tamamen keyfî sabitlerdir; hata tahmini değildir ve hiçbir yöntemin
daha doğru olduğunu ima etmez. Modülde sözleşmenin istediği `DEMO_LABEL`
("Örnek veri") sabiti bulunur.

### Çalıştırılan testler ve gerçek sonuçlar

Python 3.11.9, Windows 11. Kurulum CI ile aynı: `python -m pip install -e ".[dev]"`.

```
QT_QPA_PLATFORM=offscreen MPLBACKEND=Agg python -m pytest -q
374 passed

MPLBACKEND=Agg python -m pytest tests/visualization -q
57 passed

python tests/ui/native_smoke.py
PASS: native Windows Light/Dark, sliders, presets, Auto dt, halving,
      invalid input, methods, Run, both sizes, close.
```

374 = Kişi 3'ün güncel main üzerinde bildirdiği 317 taban + bu dalın eklediği 57
test. Mevcut hiçbir test değiştirilmedi veya kaldırılmadı.

Uygulama ayrıca gerçek bir PowerShell sekmesinden `python -m dss` ile açıldı;
pencere "Dynamic System Simulator — CMPE 443 Lab 1" başlığıyla geliyor ve girdiye
yanıt veriyor. Beklendiği gibi boş sonuç durumunu gösteriyor: üretim
`build_response_figure` M2'de, Run-to-plot bağlantısı Kişi 3'ün M4B'sindedir.

Kayıt: [`docs/evidence/visualization-m1-tests.txt`](../evidence/visualization-m1-tests.txt).

Testlerin kapsadıkları: anlaşılan açık tema renklerinin birebir doğrulanması;
Euler kimliğinin koyu temada korunması; yöntemlerin çizgi deseniyle de ayrılması;
`Exact` legend etiketi; bilinmeyen yöntem/tema için `ValueError`; donmuş
dataclass'lar; her çağrının yeni Figure döndürmesi; grid'in verinin altında
kalması ve üst/sağ spine'ların kaldırılması; metnin eğri rengini değil metin
rengini kullanması; `apply_figure_theme`'in kurulmuş figürü değiştirmesi ve eğri
rengine dokunmaması; Agg canvas üzerinde headless çizim; canvas'ın Kişi 3'ün
yaptığı gibi ayrılabilmesi; `plot_kwargs` çıktısının Matplotlib tarafından kabul
edilmesi; örnek verinin ortak doğrulayıcıdan geçmesi, deterministik olması, tek
ızgara paylaşması ve kopyalarının dışarıdan bozulamaması; alt süreçte pyplot ve
Qt'nin hiç içe aktarılmadığı.

**Görsel kontrol yapıldı.** Gerçek `solve_analytical` / `solve_euler` /
`solve_rk4` çıktıları Case 1 (a1=1, a0=1, b0=1, dt=0.6283 s) için M1 stil
tablolarıyla iki temada çizildi ve PNG olarak incelendi. Bu kontrol sonucunda
yukarıda anlatılan kalınlık ve desen düzeltmesi yapıldı. Bu görseller depoya
eklenmedi: üretim `build_response_figure` henüz yok ve ara bir betiğin çıktısı
rapor kanıtı olarak sunulmamalıdır. Rapora girecek ekran görüntüleri gerçek
uygulamadan, M4B entegrasyonundan sonra alınacaktır.

### Bilinen eksikler

- `plots.py`, `metrics.py`, `export.py` boş. M2/M3/M4 kapsamı.
- Çok küçük dt'de her örneğe işaretçi konması okunaksızdır; M2'de örnek sayısına
  göre `markevery` hesaplanacaktır.
- Koyu tema eğri renkleri Kişi 3'ün onayını bekliyor.
- `src/dss/ui/colors.py`'nin tek kaynaktan içe aktarması bir öneridir, uygulanmadı.
- CONTRIBUTING.md bu dalda genişletilmedi; M5 kapsamındadır.

### Ortam notu — Python 3.12 ile çalışmıyor, 3.11 kullanın

Bu, geliştirme sırasında karşılaşılıp çözülen bir durumdur; ekibin geri kalanını
da ilgilendirdiği için kaydediliyor.

Depo Python 3.11 hedefliyor (`.python-version`, CI). Bu makinede önce yalnız
3.12 kuruluydu ve 3.12'de **uygulama hiç açılmıyor, `tests/ui` toplanamıyor**:

```
python -c "import PySide6.QtWidgets; import matplotlib.dates"
AttributeError: '_SixMetaPathImporter' object has no attribute '_path'
```

Nedeni: PySide6 6.12.0'ın `shibokensupport` import kancası, içe aktarılan her
modül için `inspect.getsource()` çağırıyor. `matplotlib.dates` zinciri
`six.moves` sahte modülünü yüklüyor; Python 3.12 yükleyicilerdeki `module_repr()`
desteğini kaldırdığı için modülün `repr`'i `loader._path` arıyor ve `six` bunu
tanımlamıyor. Bu bir depo hatası değildir ve bu dalla ilgisi yoktur; değişmemiş
main'de aynı yorumlayıcıyla aynen tekrarlanır.

**Çözüm uygulandı:** Python 3.11.9 kuruldu, `.venv` sıfırdan 3.11 ile
oluşturuldu. Aynı tek satırlık tekrar üretim artık sorunsuz geçiyor ve tüm paket
374 passed veriyor. Depodaki sabitlenmiş 3.11'i kullanın; 3.12'ye geçilecekse
PySide6/six tarafındaki bu kancanın önce düzelmesi gerekir.

## Aşamalar arası durum kaydı

- **Sözleşme sürümü:** v0.2 (değiştirilmedi).
- **Branch:** `feat/visualization-m2`. Taban: main `e71e723` (PR #16 sonrası).
  M1, PR #15 ile main'e alındı.
- **Tamamlanan milestone:** M1, M2.
- **Sıradaki görev:** M3 — `compute_error` (yalnız y için `max_abs` ve `rmse`)
  ve `build_error_figure`. Elle hesaplanabilir örnek: `reference.y=[0,1,2]`,
  `candidate.y=[0,2,0]` → max=2, RMSE=`sqrt(5/3)`. Aynı sinyalin hatası sıfır;
  farklı ızgara örtük interpolate edilmez, açık hata verir.
- **Çalıştırılan testler:** tam paket **445 passed** (taban 402 + 43 yeni);
  `tests/visualization` toplam 100 test. Dört figür gerçek çözücü çıktısıyla
  görsel olarak incelendi.
- **Blokaj:** yok. M2 kimseyi beklemedi.
- **Başkasından beklenen API:** yok. Kişi 1 ve Kişi 2'nin çözücüleri main'de ve
  M3'ün ihtiyacı olan her şey hazır.
- **Beni bekleyenler:** Kişi 3'ün M4B-2 entegrasyonu `build_response_figure`
  (hazır), `compute_error` ve `build_error_figure` (M3) ile `export_figure`
  (M4) gerektiriyor. Rapordaki 5–6 ekran görüntüsü M4B-2'ye bağlı.
