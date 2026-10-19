# Görselleştirme — Kişi 4, M1

## Güncel milestone: M1 — bağımsız grafik altyapısı

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

```
MPLBACKEND=Agg python -m pytest tests/visualization -q
57 passed

MPLBACKEND=Agg python -m pytest tests/visualization tests/analytical tests/numerical tests/integration -q
1 failed, 301 passed
```

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

### Ortam uyarısı — bu makinede Python 3.12

Depo Python 3.11 hedefliyor (`.python-version`, CI). Bu makinede yalnız 3.12
kurulu ve 3.12'de **uygulama açılmıyor, `tests/ui` toplanamıyor**:

```
import PySide6.QtWidgets; import matplotlib.dates
AttributeError: '_SixMetaPathImporter' object has no attribute '_path'
```

Nedeni: PySide6 6.12.0'ın `shibokensupport` import kancası, içe aktarılan her
modül için `inspect.getsource()` çağırıyor. `matplotlib.dates` zinciri
`six.moves` sahte modülünü yüklüyor; Python 3.12 yükleyicilerdeki `module_repr()`
desteğini kaldırdığı için modülün `repr`'i `loader._path` arıyor ve `six` bunu
tanımlamıyor. Bu bir depo hatası değildir ve bu dalla ilgisi yoktur; değişmemiş
main'de aynı yorumlayıcıyla aynen tekrarlanır. Kişi 3'ün 3.11'de bildirdiği
317 passed sonucuyla da çelişmez.

Sonuç: bu makineye **Python 3.11 kurulmalıdır**, yoksa uygulama yerel olarak
çalıştırılamaz ve M4B sonrası ekran görüntüleri alınamaz. Görselleştirme modülü
Qt içe aktarmadığı için kendi testleri 3.12'de sorunsuz çalışır.

## Aşamalar arası durum kaydı

- **Sözleşme sürümü:** v0.2 (değiştirilmedi).
- **Branch:** `feat/visualization-m1`. Taban: main `333b377` (PR #14 sonrası).
- **Tamamlanan milestone:** M1.
- **Sıradaki görev:** M2 — `build_response_figure`; başlık, zaman/çıktı etiketi,
  legend, grid, `markevery`; bir/üç yöntem, boş liste, yanlış şekil ve farklı
  zaman ızgarası testleri; girdi dizilerinin değişmediğinin doğrulanması.
- **Çalıştırılan testler:** yukarıda; 57 passed (görselleştirme), 301 passed /
  1 pre-existing failure (Qt dışı tüm paketler).
- **Blokaj:** yok. M1 başka kimseyi beklemedi.
- **Başkasından beklenen API:** yok. M3 için Kişi 1 `solve_analytical` ve Kişi 2
  `solve_euler`/`solve_rk4` zaten main'de. M4'ün deney tablosu için Kişi 2 ile
  ortak çalışma, M4B grafik entegrasyonu için Kişi 3 gerekir.
