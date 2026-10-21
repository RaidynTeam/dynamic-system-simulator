# Görselleştirme — Kişi 4, M5

## Güncel milestone: M5 — rapor ve savunma

Durum: **M5 için TAMAMLANDI**, tek istisnayla: Kişi 3'ün PR'ını inceleme görevi
açık bir PR olmadığı için bekliyor.

Bu aşamada kod değişmedi. Teslim edilenler:

| Dosya | İçerik |
|---|---|
| [`docs/report/visualization-report.md`](../report/visualization-report.md) | Ortak rapora İngilizce katkı |
| [`docs/modules/visualization-defense-tr.md`](visualization-defense-tr.md) | Türkçe sözlü savunma rehberi |
| [`docs/modules/visualization-handoff.md`](visualization-handoff.md) | Teslim kaydı ve kalan bağımlılıklar |
| [`CONTRIBUTING.md`](../../CONTRIBUTING.md) | Ortak Git/PR kurallarının tam hâli |
| Bu dosya | Metrik tanımı, çizim/export kullanımı, test kanıtı |

### Rapor katkısı

Kişi 1 ve Kişi 2'nin rapor dosyalarıyla aynı yapıda: sorumluluk, tasarım,
uygulama/arayüzler, deneyler, sonuç, kaynaklar. İçindeki her sayı çalıştırılmış
betiklerden gelir. Kullanılan ekip katkıları (Kişi 1'in `solve_analytical`,
Kişi 2'nin çözücüleri ve bağımsız ölçüm tablosu, Kişi 3'ün `presentation.py`
sınırı ve anlaşılan renkler) kaynak olarak gösterilmiştir.

Raporda kasten **iddia edilmeyen** şey: çözücülerin kendi doğruluğu. O Kişi 1
ve Kişi 2'nin savunacağı konu; bu katkı yalnız onların çıktısının doğru
çizildiğini ve doğru ölçüldüğünü savunur.

### CONTRIBUTING

İskelet hâlindeki dosya ekip kurallarının tamamını taşıyacak şekilde
genişletildi: branch kuralları, doğrudan `main`'e push ve force push yasağı,
commit türleri ve scope listesi, commit'e girmeyecekler (`.venv`, anahtar,
uydurma test çıktısı, başkasının yazar bilgisi), PR açıklamasının beş başlığı,
review halkası, test komutları ve milestone bitiş ölçütleri.

İki madde yaşanmış sorunlardan eklendi: **halkadaki inceleyici müsait değilse**
başka bir üyenin inceleyebileceği (zorunlu olan "en az bir başka kişi" şartı) ve
sebebin PR'a yazılması; ve **Python 3.12 kullanılmaması** gerektiği.

### Savunma hazırlığı

Türkçe rehberde iki dakikalık anlatım, tahtada gösterilecek elle hesap örneği,
rehberin dört savunma sorusunun cevabı, ek sorular (neden pyplot yok, metriklerin
doğruluğu nereden biliniyor, log ekseninde sıfır, demo veri neden var) ve
**zayıf noktaların dürüst listesi** var.

## Geçmiş kayıt: M4 — export ve deney kanıtı

Durum: **M4 için TAMAMLANDI**. `export_figure` hazır. Bununla ortak sözleşmedeki
dört görselleştirme fonksiyonunun **hepsi** var: Kişi 3'ün
`load_visualization_api()` çağrısı artık başarıyla dönüyor ve M4B-2
entegrasyonunun önünde görselleştirme kaynaklı engel kalmıyor.

Ortak API v0.2 bozulmadı. Başka kişiye ait dosya değiştirilmedi.

### `export_figure`

```python
export_figure(figure, path, *, dpi=EXPORT_DPI) -> None
```

Yazma `figure.savefig` üzerinden yapılır; uzantıya göre doğru backend seçilir ve
**`figure.canvas` sonradan geri yüklenir**. Bu önemli: Kişi 3 figürü bir
`FigureCanvasQTAgg` üzerinde gösterirken kullanıcı export'a basarsa, figür o
widget'tan kopmamalı. Deneyle doğrulandı — PNG ve PDF yazımından sonra
`figure.canvas` aynı nesne kalıyor, ayrıca bir test bunu sabitliyor.

Kurallar:

- **Klasör yaratılmaz.** Sözleşme bunu UI'a bırakıyor; aksi halde yanlış yazılan
  bir yol diskte sessizce klasörler açardı. Olmayan klasör açık hata verir.
- **Tema zemini korunur.** `facecolor` açıkça geçiliyor, yoksa koyu temadaki bir
  figür beyaz sayfaya düşerdi.
- **PNG varsayılanı 200 dpi.** Ekrandaki 100 dpi rapor sayfasında yumuşak
  görünüyor. PDF vektör olduğu için dpi'dan etkilenmiyor.
- **Başarısızlık iz bırakmaz.** Bu çağrının oluşturduğu dosya hata durumunda
  silinir; **zaten var olan bir dosyaya dokunulmaz**. Hiç bayt üretmeyen bir
  yazma da başarı değil hata sayılır. Yani "boş dosya üretip başarı bildirme"
  maddesi karşılanıyor.
- Geçersiz uzantı, dizin hedefi, `Figure` olmayan girdi, takas edilmiş argüman
  sırası ve geçersiz dpi açık `ValueError` verir. Gerçek yazma hatası
  (ör. salt-okunur dosya) olduğu gibi UI'a iletilir.

### Gözle inceleme — rehberin 4. maddesi

Dışa aktarılan dosyalar üretim `export_figure`'ı üzerinden yazılıp incelendi:

- **PNG** (`case1-h0-light-response.png`, 200 dpi, 1440×900): başlık, eksen
  etiketleri ve legend tam görünüyor, hiçbiri kesilmiyor; legend veriyle
  çakışmıyor; Exact'in gri halesi RK4'ün altından ayırt ediliyor. Yazılar
  200 dpi'da net.
- **PDF** (`case1-h0-light-error-log.pdf`): **tek sayfa**, 518.4 × 324 punto =
  tam 7.2 × 4.5 inç, yani figür boyutuyla birebir. Vektör metin keskin, log
  ekseni ondalık işaretleriyle düzgün, hiçbir öğe kırpılmamış.

PDF'i görüntülemek için ortamda `poppler` yoktu; sayfa PySide6'nın `QPdfDocument`
motoruyla görüntüye çevrilip incelendi. Yani kontrol **yapıldı**, atlanmadı.

`tests/visualization/preview.py` artık `--format png|pdf|both` kabul ediyor ve
yazmayı üretim `export_figure`'ına devrediyor — incelediğin dosya, uygulamanın
Export düğmesinin üreteceği dosyanın aynısı.

### dt deney tablosu — rehberin 5. maddesi

`tests/visualization/error_experiments.py` üç Case için başlangıç adımından
başlayıp adımı beş kez yarıya indiriyor ve her seviyede gerçek çözücüleri
gerçek `compute_error` ile ölçüyor. Kayıt:
[`docs/evidence/visualization-m4-experiments.md`](../evidence/visualization-m4-experiments.md).

Kayıtta parametreler (a1, a0, b0, t0, t_end), yöntem, dt, örnek sayısı,
`max_abs`, `rmse` ve yazılım sürümleri var. **Tek bir sayı tahmin edilmemiştir.**

Sonuç — bir öncekinin hatasının bu seviyedeki hataya oranı:

| Case | Euler oranı (h0/32'de) | RK4 oranı (h0/32'de) |
|---|---:|---:|
| 1 | 2.03 | 16.09 |
| 2 | 2.02 | 16.34 |
| 3 | 2.01 | 16.70 |

Adım yarıya inince Euler'in hatası ~2 kat, RK4'ünki ~16 kat azalıyor. Bu, Euler'in
**birinci**, RK4'ün **dördüncü** mertebe olmasının deneysel karşılığıdır
(2¹ = 2, 2⁴ = 16). Teoriden türetilmedi, ölçüldü.

Kişi 2'nin `numerical-handoff.md` içindeki altı ölçümü bu tablonun ilgili
satırlarıyla her basamağına kadar örtüşüyor. **Kişi 2'nin tabloyu onaylaması
kalıyor** — rehber bu deneyin onunla birlikte hazırlanmasını istiyor.

### M4'ün bilinen eksikleri

- Rapora girecek 5–6 ekran görüntüsü hâlâ **gerçek uygulamadan** alınmalı;
  bu Kişi 3'ün M4B-2 entegrasyonuna bağlı.
- Koyu tema eğri renkleri hâlâ Kişi 3'ün onayını bekliyor.
- Deney tablosu için Kişi 2'nin onayı alınmadı.
- M5 (rapor katkısı, CONTRIBUTING) henüz yapılmadı.

## Geçmiş kayıt: M3 — hata ve metrikler

Durum: **M3 için TAMAMLANDI**. `compute_error` ve `build_error_figure` hazır.
Geriye yalnız `export_figure` (M4) kaldı; Kişi 3'ün `load_visualization_api()`
çağrısı artık eksik olarak **sadece onu** bildiriyor.

Ortak API v0.2 bozulmadı. Başka kişiye ait dosya değiştirilmedi.

### `compute_error` — sözleşmedeki iki formül

```python
compute_error(reference: Response, candidate: Response) -> ErrorMetrics
error_signal(reference: Response, candidate: Response) -> ndarray   # |Δy|
```

Sözleşme ne diyorsa o: `max_abs = max(|candidate.y − reference.y|)` ve
`rmse = sqrt(mean((candidate.y − reference.y)²))`.

**Yalnız y ölçülür.** Hız hatası kasten katılmıyor: konum ve hız hatasını tek
sayıda toplamak ikisini de anlatmayan bir sayı üretir, yönerge ise y(t) basamak
yanıtını karşılaştırıyor. **Yüzde hata da yok**: yanıt `y(0)=0`'dan başladığı
için göreli hata ilk örnekte sıfıra bölme olur.

**Sayısal bir ayrıntı:** sözleşmedeki `mean(d**2)` ifadesi `d` yaklaşık 1e154'ü
geçince float64'te taşar. Kod aynı sonucu veren ama taşmayan biçimi kullanıyor:
en büyük sapma önce dışarı çarpan olarak alınır, kareler ondan sonra hesaplanır.
Bir testte `mean(d**2)`'nin gerçekten `inf` verdiği, benim sonucumun ise sonlu
ve doğru kaldığı gösteriliyor.

### Doğrulama — iki bağımsız kaynakla eşleşiyor

**1. Rehberin elle hesaplanan örneği.** `reference.y=[0,1,2]`,
`candidate.y=[0,2,0]` → fark `[0,1,2]`, max **2.0**, RMSE **1.2909944487358056**
= `sqrt(5/3)`. Birebir tutuyor.

**2. Kişi 2'nin bağımsız ölçüm tablosu.** `docs/modules/numerical-handoff.md`
içinde Kişi 2 kendi betiğiyle altı senaryonun maksimum hatalarını ölçmüş. Benim
`compute_error`'um aynı senaryoları hesapladığında **altısı da yazılan her
basamağa kadar aynı çıkıyor**:

| Senaryo | Kişi 2'nin ölçümü (Euler) | Benim sonucum | Kişi 2 (RK4) | Benim sonucum |
|---|---|---|---|---|
| Case 1, h0 | 4.2456625100e-1 | 4.245663e-01 | 1.1940059470e-3 | 1.194006e-03 |
| Case 1, h0/32 | 7.7908424168e-3 | 7.790842e-03 | 9.7515684416e-10 | 9.751568e-10 |
| Case 2, h0 | 1.3645129660e-1 | 1.364513e-01 | 2.8790463888e-3 | 2.879046e-03 |
| Case 2, h0/16 | 6.1668402676e-3 | 6.166840e-03 | 2.3812393501e-8 | 2.381239e-08 |
| Case 3, h0 | 1.1290948247e-1 | 1.129095e-01 | 1.3349999881e-2 | 1.335000e-02 |
| Case 3, h0/8 | 6.4584911355e-3 | 6.458491e-03 | 1.1100609671e-6 | 1.110061e-06 |

İki ayrı kişi, iki ayrı kod yolu, aynı sayılar. Rehberin M3 kabul ölçütü
("metrikler bağımsız elle hesaplanan beklentiyle eşleşir") bununla karşılanıyor.
Sayılar `tests/visualization/preview.py` çıktısından; uydurulmamıştır.

### `build_error_figure`

```python
build_error_figure(reference, candidates, *, theme="light",
                   title=None, scale="linear") -> Figure
```

Her aday için `|candidate.y − reference.y|` çizilir. **Referansın kendisi
çizilmez** — kendisiyle farkı tanımı gereği sıfırdır, sıfırda düz bir çizgi
yalnız legend'i kalabalıklaştırırdı. Eksen etiketi ve başlık referansın adını
kullanır (`Absolute error vs Exact`), yani referans değişirse etiket de değişir.

**Eksen ölçeği.** Varsayılan doğrusal — rehberin istediği gibi. Fakat doğrusal
eksende RK4'ün hatası Euler'in yanında sıfır gibi görünüyor (Case 1'de 1.2e-3'e
karşı 4.2e-1). Bu yüzden `scale="log"` seçeneği var ve rehberin istediği açıklama
şu: **log ekseni sıfır değeri gösteremez.** İlk örnekte hata her zaman tam
sıfırdır, çünkü bütün çözücüler aynı `y(0)=0` koşulundan başlar. Bu örnekler
*maskelenir*: eğri orada kesilir, yerine uydurma bir taban değeri konmaz ve
eksende olmayan bir noktaya doğru çizgi çizilmez. Sıfırlar verinin içinde kalır.
İlk denemede maskeleme yoktu ve sol kenarda hayalet bir dikey çizgi oluşuyordu;
görsel kontrolde yakalandı.

### Reddedilen girdiler

| Girdi | Neden |
|---|---|
| Boş aday listesi | Çizilecek bir şey yok |
| `Response` olmayan referans/aday | Ortak sözleşme dışı |
| Aynı yöntem iki kez, ya da referansla aynı yöntemde aday | Legend belirsizleşir |
| Farklı zaman ızgarası | **Örtük interpolasyon yapılmaz**, açık hata |
| Bilinmeyen `scale`/`theme`, boş `title` | Anlamsız çıktı yerine hata |

### Çalıştırılan testler ve gerçek sonuçlar

```
QT_QPA_PLATFORM=offscreen MPLBACKEND=Agg python -m pytest -q
525 passed

MPLBACKEND=Agg python -m pytest tests/visualization -q
180 passed
```

525 = M2 sonrası 445 + bu dalın 80 testi (24 metrik, 56 hata grafiği). Mevcut
hiçbir test değiştirilmedi.

Görsel kontrol `tests/visualization/preview.py` ile yapıldı; betik artık her
senaryo için üç dosya üretiyor: yanıt, hata (doğrusal), hata (log). Ayrıca
ölçülen maksimum hataları konsola yazıyor — yukarıdaki tablo oradan.

### M3'ün bilinen eksikleri

- `export.py` hâlâ boş (M4). Kişi 3'ün entegrasyonunun önündeki **tek** engel bu.
- Koyu tema eğri renkleri hâlâ Kişi 3'ün onayını bekliyor.
- Metrikler figürün legend'ına yazılmıyor; Kişi 3'ün ayrı metrik paneli var.

## Geçmiş kayıt: M2 — yanıt karşılaştırması

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

**Görsel kontrol yapıldı.** Otomatik testler sayıyı, etiketi ve nesne kimliğini
doğrular; bir figürün *okunabilir* olup olmadığını söyleyemez. Bunun için
`tests/visualization/preview.py` eklendi — Kişi 2'nin
`tests/numerical/experiments.py` betiğiyle aynı kalıpta:

```
python tests/visualization/preview.py            # PNG'leri geçici klasöre yazar
python tests/visualization/preview.py --open     # yazıp klasörü açar
python tests/visualization/preview.py <klasör> --theme both
```

(Betik M3'te genişletildi: artık senaryo başına üç dosya üretiyor ve ölçülen
maksimum hataları da yazdırıyor. Ayrıntı M3 bölümünde.)

Betik üretim `build_response_figure`'ını gerçek çözücü çıktısıyla çağırır ve
`docs/modules/numerical-handoff.md` içinde Kişi 2'nin rapor ekran görüntüleri
için önerdiği **altı senaryoyu** çizer: üç Case, her biri başlangıç adımı `h0`
ve bir kez küçültülmüş adımla (h0/32, h0/16, h0/8). Çıktı varsayılan olarak
sistem geçici klasörüne yazılır, depoya hiçbir şey bırakmaz.

İncelenen sonuçlar: Case 1'de Euler'in aşımı ve salınımı, Case 2'de aşımsız
kritik sönümlü yükseliş, Case 3'te aşımsız monoton yükseliş — üçü de beklendiği
gibi. Küçültülmüş adımda üç eğri çakışıyor. İşaretçi seyreltme N=1020'de doğru
çalıştı; Exact eğrisi RK4'ün altından her iki temada da görünüyor.

Bu görüntüler depoya eklenmedi — rapora girecek ekran görüntüleri **gerçek
uygulamadan**, Kişi 3'ün M4B-2 entegrasyonundan sonra alınacak.

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

- **Sözleşme sürümü:** v0.2 (hiç değiştirilmedi).
- **Branch:** `feat/visualization-m5`, güncel main `373b1f3` üzerinden açıldı.
  M1 PR #15, M2 PR #17, M3 PR #18, M4 PR #19 ile main'de.
- **Tamamlanan milestone:** M1, M2, M3, M4, M5.
- **Sıradaki görev:** Kişi 3'ün M4B-2 PR'ını incelemek (halka: Kişi 4 → Kişi 3).
  Kontrol anında açık PR yoktu.
- **Çalıştırılan testler:** tam paket **565 passed**; `tests/visualization`
  toplam **220 test** (24 kimlik/tema, 20 figür, 11 örnek veri, 2 izolasyon,
  43 yanıt grafiği, 24 metrik, 56 hata grafiği, 40 export). M5'te kod
  değişmedi, sayılar M4'tekiyle aynı.
- **Blokaj:** yok. Beş milestone'un hiçbiri başka kimseyi beklemedi.
- **Başkasından beklenen API:** yok.
- **Benim beklediklerim** (ayrıntı: [teslim kaydı](visualization-handoff.md)):
  - Kişi 3: koyu tema eğri renklerinin onayı; M4B-2 entegrasyonu; `ui/colors.py`
    için tek kaynak renk önerisi.
  - Kişi 2: dt deney tablosunun onayı.
  - Ortak: gerçek uygulamadan 5–6 ekran görüntüsü, raporun birleştirilmesi,
    RAR teslim paketi.
