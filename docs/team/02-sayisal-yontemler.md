# Kişi 2 — Euler, RK4 ve test altyapısı

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

`numerical/`, `tests/numerical/`, `pyproject.toml` ve CI senin alanındır. Ortak `contracts.py` Kişi 1'e aittir. GUI, analitik çözüm veya çizim modülünü yeniden yazma. Paket yapılandırmasında herkesin ihtiyaç duyduğu bağımlılıkları topla.

**İş yükü: 16 göreli puan.** Paket/ızgara 3, Euler 3, RK4 4, test/CI 4, dokümantasyon/review 2. Sayısal algoritma yükü arttığında ek özellik eklemek yerine kapsamı koru.

## 7. Adım adım geliştirme

### M1 — Paket ve zaman ızgarası (3 puan)
1. Varsa mevcut paket yapılandırmasını kullan; yoksa `src/dss` düzenini kurulabilir hale getir. Bağımlılıkları ve geliştirme test bağımlılıklarını kaydet.
2. Kişi 1'in tiplerini kullanacak `make_time_grid` tasarımını hazırla.
3. `0..1, dt=0.3` için `[0,0.3,0.6,0.9,1]`; `0..1,dt=2` için `[0,1]` bekle. Kayan nokta karşılaştırmasını toleranslı yap.
4. Tam bölünebilen aralık, kaydırılmış `t0`, çok küçük adım ve örnek sınırını test et.

**Kabul:** Kurulum ve test komutu belgelenir; zaman aralığının dışına çıkan veya yinelenen örnek yoktur.

### M2 — Euler (3 puan)
1. `z=[y,v]`, `f(z)=[v,b0-a1*v-a0*y]` fonksiyonunu tek yerde uygula.
2. Her adım için `h=t[i+1]-t[i]` ve `z_next=z+h*f(z)` kullan.
3. y ve v güncellemeleri aynı eski durumu kullanmalıdır; güncellenmiş y'yi hız hesabında kullanmak açık Euler'i değiştirir.
4. Son kısa adımı, girişlerin değiştirilmemesini ve hesap taşmasını denetle.

**Kabul:** Tek adım elle hesaplanan referansla eşleşir; ilk örnek başlangıç koşullarıdır.

### M3 — RK4 (4 puan)
1. Aynı durum vektörü ve aynı RHS üzerinde `k1=f(z)`, `k2=f(z+h*k1/2)`, `k3=f(z+h*k2/2)`, `k4=f(z+h*k3)` hesapla.
2. `z_next=z+h*(k1+2*k2+2*k3+k4)/6` uygula. k'ların türev olduğunu, h'nin sonradan çarpıldığını koru.
3. Her alt aşamada iki durum bileşenini birlikte ilerlet; Euler fonksiyonunu RK4 diye etiketleme.
4. Euler ve RK4 için ortak doğrulama kullan; yöntemlerin kendi adım mantığını okunabilir tut.

**Kabul:** Bilinen çözümde RK4 daha küçük hata verir; iki çözücü aynı dış ızgarayı kullanır.

### M4 — Yakınsama, kararlılık ve CI (4 puan)
1. Bağımsız referans olarak `a1=2,a0=1,b0=1` için `y=1-(1+t)*exp(-t), v=t*exp(-t)` çözümünü kullan; test için Kişi 1'in kodunun hazır olması gerekmez.
2. `T=1`, `h=0.1,0.05,0.025` için son nokta y hatalarını kaydet. Asimptotik bölgede `E(h)/E(h/2)` Euler için yaklaşık 2, RK4 için yaklaşık 16 beklenir. Ölçülen oranları kaydet; makul aralıkları veriyle gerekçelendir ve yuvarlama tabanındaki oranları başarı ölçütü yapma.
3. Üç lab Case’i, düzensiz artan ızgara, son kısa adım, geçersiz giriş ve taşmayı test et.
4. Açık Euler'in kararlılık kısıtını belgede açıkla: `z'=lambda*z` için `abs(1+h*lambda)<1`. Büyük adımda fiziksel sistem sönümlü olsa da sayısal çözüm büyüyebilir; bunu sessiz düzeltme veya adımı gizlice değiştirme.
5. PR'larda kurulum ve testleri çalıştıran CI hazırla; gerçek test sonucu olmadan yeşil durum iddia etme. GUI/grafik headless ayarlarını ilgili sahiplerle eşleştir.

**Kabul:** Yakınsama ölçümü ve testler tekrar üretilebilir; CI yapılandırması ile gerçekten çalışan CI ayrıştırılmıştır.

### M5 — Teslim ve savunma (2 puan)
`docs/modules/numerical.md` içine algoritma, yakınsama tablosu, kararlılık sınırı, kurulum/test komutlarını yaz. Ortak rapora yöntem ve deney tablosu ver. Kişi 4'ün PR'ını incele.

**Savunma soruları:** Euler ve RK4'ün farkı nedir? Yerel ve global hata nasıl ayrılır? Son adım neden kısalabilir? Kararsız sayısal sonuç her zaman kararsız fiziksel sistem midir?

## 8. Tamamlanma ve ilk görev

- [ ] Paket kurulumu ve ortak zaman ızgarası hazır.
- [ ] Euler/RK4 aynı model ve aynı ızgara üzerinde çalışıyor.
- [ ] Yakınsama, son kısa adım ve taşma testleri doğrulandı.
- [ ] CI, test kanıtı ve rapor katkısı hazır.

Örnek commitler: `feat(numerical): add bounded time grid`, `feat(numerical): implement coupled rk4 steps`, `ci(project): run tests on pull requests`.

**Ajana ilk görev:** M1 ile başla; repo yapılandırmasını incele, ortak tipler için Kişi 1'in sözleşmesine uy ve zaman ızgarasının uç durumlarını bağımsız tasarla. Kişi 1'in tüm analitik modülünü bekleme.
