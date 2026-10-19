# Kişi 1 — Analitik çözümler ve model sözleşmesi

**Sürüm:** 1.1 · **Hazırlanma:** 19 Ekim 2026 · **Ortak API:** v0.2

Bu belge tek başına paylaşılabilir. Proje bağlamı, ortak sözleşme, ekip kuralları ve sana özel aşamalar burada birlikte bulunur. Kendi yapay zekâ ajanına dosyanın tamamını yükle; yalnız son görev listesini verme. Rolünü başka bir kişiyle değiştirirsen ajana yeni rol belgesini ver.

## 1. Proje bağlamı ve bilginin güvenilirliği

Proje: **Dynamic System Simulator — Lab 1**, dört kişilik ortak Python uygulaması.
Konuşmada belirtilen depo: https://github.com/RaidynTeam/dynamic-system-simulator
Bu belge depoya bağlanılarak hazırlanmadı; mevcut dosyalar, erişimler ve GitHub kuralları doğrulanmış değildir.
Teknoloji planı: Python, NumPy, PySide6, Matplotlib, pytest. Python 3.11+ başlangıç önerisidir; mevcut depo farklı bir sürüm kullanıyorsa önce onu incele. Bağımlılık sürümleri kurulumda birlikte belirlenip kaydedilecek.

Asıl yönerge artık `docs/reference/Lab1-RTS-09102026.pdf` altında mevcuttur. Kaynak: sayfa 1–2 model ve Case formülleri; sayfa 5 görevler; sayfa 6 teslim/rapor koşulları. Teslim 26 Ekim 2026 Pazartesi 08.00; notlandırma %40 rapor, %60 uygulamayı açıklama; raporda 5–6 ekran görüntüsü istenir. PDF saat dilimini ayrıca belirtmez.

Bu paket bir geliştirme planıdır; deney sonuç raporu değildir. Üye isimleri bilinmediğinden Kişi 1–4 kullanılır.

### Doğrulanmış lab modeli

`y'' + a1*y' + a0*y = b0*x(t)`, `x(t)=1` (t>=0), `y(0)=v(0)=0`.
Kullanıcı parametreleri `a1>0`, `a0>0`, `b0>0`; hepsi sonlu olmalıdır.
`a2`, `u0`, `y0`, `v0` artık ModelParams alanları değildir. Önceki genel model önerisi bu özel lab kapsamıyla değiştirilmiştir. API v0.2 kullanın.

`D=a1²-4*a0`: D<0 → Case 1, D=0 → Case 2, D>0 → Case 3.
PDF örnekleri `(a1,a0)=(1,1),(2,1),(3,1)`; b0 için pozitif değer seçilir. Tüm çözümlerin limiti `b0/a0` olur.
Lab başlangıç adımı `T=0.1*2*pi/sqrt(a0)`; sayısal ve analitik sonuçlar uyuşmuyorsa adım yarıya indirilerek karşılaştırma tekrarlanır. “İyi uyuşma” için sayısal tolerans PDF'de tanımlanmamıştır; ekip ölçütü ayrıca belgelenir.

## 2. Ortak mimari, dosya sahipliği ve bağımlılıklar

```text
src/dss/
  __init__.py
  contracts.py             Kişi 1: ortak veri tipleri ve doğrulama
  analytical/              Kişi 1: analitik çözüm ve kök sınıflandırması
  numerical/               Kişi 2: zaman ızgarası, Euler, RK4
  ui/                      Kişi 3: PySide6, controller, grafik yerleştirme
  __main__.py              Kişi 3: uygulama giriş noktası
  visualization/           Kişi 4: Figure, hata metrikleri ve dışa aktarma
  demo_data.py             Kişi 4: yalnız geliştirme/test için örnek eğriler
tests/
  analytical/              Kişi 1
  numerical/               Kişi 2
  ui/                      Kişi 3
  visualization/           Kişi 4
  integration/             Kişi 3: herkesin desteklediği uçtan uca testler
docs/
  lab-requirements.md       Kişi 1: yönerge eşleştirmesi
  modules/                 Herkes kendi modül açıklaması
  evidence/                Herkes kendi test/grafik kanıtı
pyproject.toml             Kişi 2: paket, bağımlılık ve test ayarları
.github/workflows/        Kişi 2: CI
README.md                 Kişi 3: kurulum ve çalıştırma
CONTRIBUTING.md            Kişi 4: Git ve PR süreci
```

Bunlar oluşturulacak dosyaların planıdır, mevcut dosyalar değildir. Mevcut depo eşdeğer bir yapıya sahipse gereksiz yere yeniden kurma. Ortak dosyanın sahibi tek kişidir; diğerleri değişiklik önerisini ona iletir. Sözleşme değişirse dört rehberin ortak metni de aynı sürüme güncellenir. Başkasının modülünü kopyalayıp ikinci bir uygulama yazma.

Bağımlılık yönü: `contracts → analytical/numerical/visualization → ui`. Matematik modülleri Qt veya Matplotlib içe aktarmaz. Visualization Qt gerektirmeden Figure üretir; Qt canvas uyarlaması UI'dadır. Döngüsel import oluşturma.

## 3. Ortak sözleşme v0.2 — dört belgede aynıdır

Bu bölüm API v0.2 sözleşmesidir. M1: ortak tipler, doğrulamalar ve sınıflandırma uygulanmıştır; M2 branch’inde solve_analytical yalnız Case 2 için uygulanmıştır. Case 1/3 açık NotImplementedError üretir; grafik/controller fonksiyonları sonraki aşamaların tasarımıdır. Diziler NumPy float64, zaman ve sonuçlar sonlu değerlerdir. `ModelParams`, `SimulationConfig`, `Response`, `ErrorMetrics` frozen dataclass olarak uygulanmıştır. ErrorMetrics iki sonlu, negatif olmayan skaler alır; metrik hesaplaması M1 kapsamında değildir. Aşağıdaki isimler ve alanlar bütün modüllerde aynı kullanılacaktır.

```python
ModelParams(a1: float, a0: float, b0: float)
SimulationConfig(t0: float, t_end: float, dt: float)
Response(t: np.ndarray, y: np.ndarray, v: np.ndarray, method: str)
ErrorMetrics(max_abs: float, rmse: float)

# dss.contracts — Kişi 1
validate_model(model: ModelParams) -> None
validate_config(config: SimulationConfig) -> None
validate_response(response: Response) -> None

# dss.analytical — Kişi 1
solve_analytical(model: ModelParams, t: np.ndarray) -> Response
classify_roots(model: ModelParams) -> str
classify_case(model: ModelParams) -> Literal[1, 2, 3]

# dss.numerical — Kişi 2
make_time_grid(config: SimulationConfig) -> np.ndarray
solve_euler(model: ModelParams, t: np.ndarray) -> Response
solve_rk4(model: ModelParams, t: np.ndarray) -> Response

# dss.visualization — Kişi 4
compute_error(reference: Response, candidate: Response) -> ErrorMetrics
build_response_figure(responses: list[Response]) -> matplotlib.figure.Figure
build_error_figure(reference: Response,
                   candidates: list[Response]) -> matplotlib.figure.Figure
export_figure(figure: matplotlib.figure.Figure, path: pathlib.Path) -> None

# dss.demo_data — Kişi 4
make_demo_responses() -> list[Response]

# dss.ui.controller — Kişi 3
run_simulation(model: ModelParams, config: SimulationConfig,
               methods: tuple[str, ...]) -> list[Response]
```

- `ModelParams` tam olarak `a1`, `a0`, `b0` alır; üçü de sonlu ve pozitiftir. Geçersiz değerler yapıcıda `ValueError` üretir. Sıfır başlangıç koşulu ve birim basamak lab kapsamında sabittir.
- Config için `t0 == 0`, `t_end > 0`, `dt > 0`; bütün değerler sonlu. Config yapıcıda doğrulanır. Zaman birimi proje örneklerinde saniyedir; fiziksel katsayı birimleri yönergeden doğrulanacaktır.
- Izgara `t0` ile başlar, `t_end` ile biter ve kesin artar. Tam adımlar `t0+k*dt` üzerinden hesaplanır; gerekirse son adım kısalır. Yuvarlama nedeniyle yinelenen son örnek üretilmez. Adım sayısı önceden hesaplanır; 1.000.000'dan fazla örnek istenirse `ValueError` verilir. Bu sınır ürün tercihi olup ortak değiştirilebilir.
- Çözücüler aynı `t` dizisini alır; `t` en az iki örnektir, bir boyutlu, sonlu ve kesin artandır. `t[0] == 0` olmalıdır. Bütün çözücüler ilk örnekte `y=v=0` koşulunu uygular.
- Response içindeki `t`, `y`, `v` şekli `(N,)` ve uzunlukları eşittir. Girdileri yerinde değiştirme. Response yapıcısı doğrulanmış dizilerin kopyalarını alır; diziler değiştirilebilir fakat girdi belleğini paylaşmaz. Response alanları frozen dataclass ile sabittir. `method` yalnız `analytical`, `euler`, `rk4` değerlerinden biridir.
- `classify_roots` çıktısı `distinct_real`, `repeated_real` veya `complex_conjugate` olur. `classify_case` bunları sırasıyla Case 3, 2, 1 ile eşler. Pozitif katsayılarla tüm lab sistemleri kararlıdır. Sınıflandırma `(a1/s)²-(2*sqrt(a0)/s)²`, `s=max(a1,2*sqrt(a0))` üzerinden yapılır; mutlak değer `64*float64_epsilon` veya altındaysa kritik kabul edilir. Bu ölçekli sayısal toleranstır; sembolik eşitlik iddiası değildir.
- Geçersiz giriş `ValueError`; hesap sırasında taşma/NaN/Inf `FloatingPointError` üretir. Desteklenmeyen doğrulanmış lab girdisi varsa `NotImplementedError` açık mesajla kullanılır; sahte sonuç dönülmez.
- Hata metrikleri yalnız **y** için: `max_abs=max(abs(candidate.y-reference.y))`, `rmse=sqrt(mean((candidate.y-reference.y)**2))`. Karşılaştırılan `t` dizileri aynı şekil ve aynı elemanlara sahip olmalıdır (`np.array_equal`); örtük interpolasyon yapılmaz. Sıfıra bölme riski nedeniyle yüzde hata varsayılan değildir.
- Figure üreticileri boş listeyi reddeder; karşılaştırmalı çizimde aynı zaman ızgarasını doğrular. `build_error_figure`, her aday için `abs(candidate.y-reference.y)` çizer. Legend, zaman ekseni, çıktı etiketi ve başlık gerekir. Fiziksel birim bilinmiyorsa tahmini birim yazılmaz.
- Dışa aktarım `.png` ve `.pdf` destekler; var olan dosya için kullanıcı onayı UI tarafından alınır. `export_figure` klasör yaratmaz; yazma hatasını UI'ya iletir. Global `plt.show()` çağrılmaz.
- Controller, boş veya tekrarlı `methods` listesini ve bilinmeyen yöntem adını reddeder; sırayı korur. Bir kez ızgara üretip bütün seçili çözücülere verir. Başarısız yöntemi sessizce atlayıp eksik başarılı sonuç sunmaz; hatayı UI'ya iletir.
- `make_demo_responses` aynı ızgarada üç yöntem etiketi taşıyan, deterministik örnek Response listesi üretir. Bunlar gerçek çözücü çıktısı veya doğruluk kanıtı değildir; UI'da görünür “Örnek veri” etiketi bulunur.

### Paralel çalışmanın başlangıç kuralı

Kişi 1 ilk küçük PR'da `contracts.py` ve temel doğrulama testlerini; Kişi 2 paket iskeletini sağlar. Bunlar kısa başlangıç bağımlılıklarıdır. Bu sırada Kişi 3 arayüz akışını, Kişi 4 NumPy örnek eğrilerini tasarlar. Ortak tipler birleştikten sonra herkes kendi branch'ini günceller. Geçici test double'ları yalnız test veya demo alanında tutulur; üretim sözleşmesinin ikinci kopyası oluşturulmaz. Hiçbir rol diğerinin tüm modülünün bitmesini beklemez.

## 4. Git, PR ve ortak tamamlanma kuralları

- `main` dağıtıma/teslime hazır sürümdür. Geliştirme ayrı branch'te yapılır; merge PR üzerinden ve en az bir başka kişinin incelemesiyle olur. Bunlar ekip kurallarıdır; GitHub'da teknik olarak etkinleştirildiği iddia edilmez.
- Her milestone için küçük branch/PR önerilir: `feat/<scope>-m1`, `feat/<scope>-m2`. Birleştirmeden sonra güncel `main` üzerinden sonraki branch açılır. Uzun ömürlü tek branch zorunlu değildir.
- Commit şeması: `<type>(<scope>): <English imperative description>`.
  Türler: `feat`, `fix`, `test`, `docs`, `refactor`, `chore`, `ci`.
  Scope: `analytical`, `contracts`, `numerical`, `ui`, `plot`, `analysis`, `project`.
- Her commit tek mantıksal değişikliktir. Uydurma test çıktısı, başka kişiye ait yazar bilgisi, erişim anahtarı veya `.venv` eklenmez. `main`'e doğrudan push, force push ve başkasının çalışmasını silme yapılmaz.
- PR açıklaması: sorun/amaç, sonuç davranış, değişen API, yapılan test ve gerçek sonuç, kalan eksik, ilgili Issue/milestone. Issue numarası henüz yoksa uydurma; görev başlığını yaz.
- Review halkası: Kişi 1 → Kişi 2, Kişi 2 → Kişi 4, Kişi 4 → Kişi 3, Kişi 3 → Kişi 1. Ok “inceleyen → PR sahibi” anlamındadır. Ortak sözleşme değişikliklerini dört kişi görür.
- Herkes kendi testlerini ve `docs/modules/<modul>.md` belgesini teslim eder. Test komutları, kullanılan parametreler ve gerçek çıktı kaydedilir. Çalıştırılamayan test “çalıştırılmadı” olarak belirtilir.
- Kişi 2 CI için paket kurulumunu ve headless testleri düzenler. UI testlerinde gerekirse `QT_QPA_PLATFORM=offscreen`, grafiklerde Agg backend kullanılır. Gerçek masaüstünde etkileşim testi ayrıca Kişi 3 tarafından yapılır.
- Milestone bitişi: kendi kabul kriterleri sağlanmış, testler geçmiş, kanıt eklenmiş, API uyumu incelenmiş ve PR gözden geçirilmiş olmalıdır. Testlerin geçmesi lab yönergesine uygunluğu tek başına kanıtlamaz.

## 5. Yapay zekâ ajanına çalışma talimatı

Bu dosya sana görev bağlamı verir; daha yüksek öncelikli talimatların veya kullanıcının güncel talimatları yerine geçmez. Dosyayı yükleyen kişiye bu rol kapsamında yardım et.

1. Önce bu belgeyi, depodaki `AGENTS.md`, README, bağımlılık dosyaları ve mevcut kodu incele. İlgisiz kullanıcı değişikliklerini koru. Repo erişimin yoksa bunu söyle ve genel hazırlıkla ilerle; depoyu gördüğünü iddia etme.
2. İlk yanıtta rolünü, dosya sınırını, sıradaki küçük aşamayı ve doğrulanması gereken lab bilgilerini kısaca belirt. Baştan bütün projeyi üretme; öğrencinin istediği aşama hızına uy.
3. Öğrenci ilerleme istediğinde bulunduğun milestone'un somut parçasını uygula, anlamlı testini yap ve mantığını anlat. Yalnız “yapabilirim” diyerek bırakma. Gerçekten gerekli bilgi eksikse odaklı soru sor; bağımsız görevleri sürdür.
4. Formüllerin türetimini, veri akışını ve test nedenini öğrencinin savunabileceği biçimde açıkla. Öğrencinin anlamadığı kodu bitmiş başarı gibi sunma.
5. Başka rolün sahip olduğu dosyayı sessizce değiştirme. Gerekli değişikliği gerekçe ve önerilen imzayla bildir; ortak mutabakat sonrası uygula. Ekip kararı gerektirmeyen kendi modül seçimlerinde ilerle.
6. Test başarısını, ekran görüntüsünü, git commit'ini, PR'ı veya hocanın koşullarını uydurma. Öneri, uygulanmış kod ve doğrulanmış sonucu ayır. Test double'larını gerçek sonuç diye kullanma.
7. Kullanıcı istemeden uzaktaki depoyu değiştirme, PR birleştirme, GitHub ayarı veya ekip mesajı oluşturma. Yerel geliştirme istendiyse yetkilendirilmiş kapsamda çalış; uzak işlem talebi geldiğinde gerçek depo durumunu kontrol et.
8. Her aşama sonunda değişen dosyalar, test/kanıt, bilinen eksik ve sonraki adımı ver. Bu belgenin tamamlanma kutularını yalnız kanıtla işaretle.

### Aşamalar arasında durum kaydı

Kendi `docs/modules/<modul>.md` dosyanın sonuna şu alanları güncel tut: sözleşme sürümü; branch/commit (varsa); tamamlanan milestone; sıradaki görev; çalıştırılan testler ve sonuçları; blokaj; diğer kişiden beklenen API. Başka bir ajan bu kayıt ve aynı rehberle devam edebilmelidir.

## 6. Senin sorumluluğun

Analitik çözümü, ortak model doğrulamasını ve karakteristik kök sınıflandırmasını geliştir. `contracts.py`, `analytical/`, `tests/analytical/`, sözleşme testleri ve `docs/lab-requirements.md` senin alanındır. Sayısal çözücü, GUI veya çizim kodu yazmak senin görevin değildir.

**İş yükü: 16 göreli puan.** Ortak sözleşme 3, matematik/çözüm 7, doğrulama 4, dokümantasyon/review 2. Bunlar saat tahmini değildir; M2 sonunda ekip gerçekleşen yükü yeniden değerlendirir.

## 7. Adım adım geliştirme

### M1 — Sözleşme ve model (3 puan)
1. Mevcut repo yapısını kontrol et; ortak tipleri ve doğrulamaları küçük PR ile sun.
2. Denklemi `z=[y,v]` ve `z'=[v,b0-a1*v-a0*y]` biçimine dönüştür.
3. `r²+a1*r+a0=0` köklerini ve başlangıç koşullarının anlamını açıkla.
4. Yönergeye göre üç Case için denklem, katsayı, giriş, başlangıç koşulu ve beklenen çıktıları kaynakla tabloya koy. Kaynak sayfa ve formül numarasını kaydet.

**Kabul:** Ortak tipler üzerinde diğer üç kişi çalışabilir; geçersiz parametreler tutarlı hata verir.

### M2 — Bir analitik senaryo (4 puan)
1. Önce Case 2'yi PDF (9) üzerinden uygula: `sigma=a1/2`, `K=b0/a0`, `y=K*(1-exp(-sigma*t)*(1+sigma*t))`.
2. Türevini de döndür: `v=K*sigma²*t*exp(-sigma*t)`.
3. Başlangıç koşulları ve `b0/a0` limitini bağımsız beklenen değerlerle test et.

### M3 — Diğer iki Case (3 puan)
1. Case 1 için PDF (8), Case 3 için PDF (10) formüllerini uygula.
2. y ve v çıktılarında aynı zaman ızgarasını koru.
3. Kritik sınıra yakın bölmede sıfır/iptal hatası riskini incele. M1 sınıflandırma toleransına uy.
4. Lab dışındaki sıfır/negatif katsayı veya farklı başlangıç koşullarını desteklemek bu görev değildir.

### M4 — Bağımsız doğruluk kanıtı (4 puan)
- PDF'deki üç örneği `b0=1` ile çalıştır; y(0)=v(0)=0 ve son değer 1 olmalı.
- b0 ölçeklenince y ve v aynı oranda ölçeklenmeli.
- Kritik sınıra iki yandan yaklaşırken çıktının davranışını kontrol et.
- İyi koşullu kısa aralık örnekleri için başlangıç hedefi `rtol=1e-8, atol=1e-10`; toleransı gerekçelendir.
- Beklenen analitik değerleri sayısal çözücüden kopyalama.

### M5 — Teslim ve savunma (2 puan)
Analitik türetim, kapsam, tolerans ve test kanıtını `docs/modules/analytical.md` içine yaz. Ortak lab raporuna model/türetim bölümü ver. Kişi 2'nin PR'ını incele.

**Savunma soruları:** Özel çözüm neden ayrılır? Tekrarlı kök neden farklıdır? Başlangıç koşulları iki sabiti nasıl belirler? Kararlılık ile kök sınıfı arasındaki fark nedir?

## 8. Tamamlanma ve ilk görev

- [ ] Sözleşme ve doğrulamalar birleştirildi.
- [ ] Bütün desteklenen kök/özel durum dalları test edildi.
- [ ] Yönerge eşleştirmesi doğrulandı veya açık eksik olarak kaydedildi.
- [ ] Türetim, test çıktısı ve rapor katkısı teslim edildi.

Örnek commitler: `feat(contracts): define shared response models`, `feat(analytical): handle repeated roots`, `test(analytical): verify zero-state step response`.

**Ajana ilk görev:** M1 ile başla; önce mevcut depoyu incele, ortak API tasarımını mevcut yapıyla eşleştir ve en küçük sözleşme değişikliğini hazırla. PDF sayfa 1–2 ve 5 modelin kaynağıdır.
