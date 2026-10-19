# Kişi 3 — PySide6 arayüzü ve uygulama entegrasyonu

**Sürüm:** 1.0 · **Hazırlanma:** 19 Ekim 2026 · **Ortak API:** v0.1

Bu belge tek başına paylaşılabilir. Proje bağlamı, ortak sözleşme, ekip kuralları ve sana özel aşamalar burada birlikte bulunur. Kendi yapay zekâ ajanına dosyanın tamamını yükle; yalnız son görev listesini verme. Rolünü başka bir kişiyle değiştirirsen ajana yeni rol belgesini ver.

## 1. Proje bağlamı ve bilginin güvenilirliği

Proje: **Dynamic System Simulator — Lab 1**, dört kişilik ortak Python uygulaması.
Konuşmada belirtilen depo: https://github.com/RaidynTeam/dynamic-system-simulator
Bu belge depoya bağlanılarak hazırlanmadı; mevcut dosyalar, erişimler ve GitHub kuralları doğrulanmış değildir.
Teknoloji planı: Python, NumPy, PySide6, Matplotlib, pytest. Python 3.11+ başlangıç önerisidir; mevcut depo farklı bir sürüm kullanıyorsa önce onu incele. Bağımlılık sürümleri kurulumda birlikte belirlenip kaydedilecek.

Önceki konuşmada üç Case, analitik/Euler/RK4 karşılaştırması, 26 Ekim 2026 08.00 teslimi, 5–6 ekran görüntüsü ve %60 savunma ağırlığı anılmıştır. **Asıl lab yönergesi elde olmadığı için bunların hiçbiri burada doğrulanmış ders koşulu sayılmaz.** Tarih için yerel saat Asia/Famagusta esas alınır; kesin saat dilimi de yönergeden kontrol edilmelidir.

Bu paket bir geliştirme planıdır; tamamlanmış uygulama veya deney sonuç raporu değildir. Üye isimleri bilinmediğinden Kişi 1–4 kullanılır. İsimler daha sonra rol dağılımına eklenebilir.

### Model için açık tasarım varsayımı

Ortak başlangıç modeli aşağıdaki sabit katsayılı, sabit girişli ikinci dereceden denklemdir:

`a2 * y''(t) + a1 * y'(t) + a0 * y(t) = u0`, `y(t0)=y0`, `y'(t0)=v0`.

Bu denklem **ekibin başlangıç tasarım önerisidir**, hocanın üç Case tanımı değildir. Üç Case'i otomatik olarak az/kritik/aşırı sönümlü kabul etme. Yönergedeki denklemler, giriş türleri, başlangıç koşulları, birimler ve zorunlu grafikler elde edildiğinde `docs/lab-requirements.md` içinde kaynağıyla eşleştir. Bir Case bu modele sığmıyorsa sözleşme değişikliğini ortaklaştır; yerel bir çözümle farklı API üretme. Bu belirsizlik arayüz taslağı, örnek veri, genel çözücü ve test tasarımını durdurmaz; doğrulanmamış Case presetlerini gerçek lab seçeneği gibi sunma.

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

## 3. Ortak sözleşme v0.1 — dört belgede aynıdır

Bu bölüm uygulanacak API tasarımıdır; hazır kod değildir. Diziler NumPy float64, zaman ve sonuçlar sonlu değerlerdir. `ModelParams` ve `SimulationConfig` dondurulmuş dataclass olarak tasarlanır. Aşağıdaki isimler ve alanlar bütün modüllerde aynı kullanılacaktır.

```python
ModelParams(a2: float, a1: float, a0: float, u0: float,
            y0: float, v0: float)
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

- Modelde bütün sayılar sonlu ve `a2 > 0` olmalıdır. `a1`, `a0`, `u0`, `y0`, `v0` sıfır veya negatif olabilir. Kararsız fakat matematiksel olarak geçerli modelleri gizlice engelleme. Bu kapsama uymayan yönerge modeli sözleşme revizyonudur.
- Config için `t_end > t0`, `dt > 0`; bütün değerler sonlu. Zaman birimi proje örneklerinde saniyedir; fiziksel katsayı birimleri yönergeden doğrulanacaktır.
- Izgara `t0` ile başlar, `t_end` ile biter ve kesin artar. Tam adımlar `t0+k*dt` üzerinden hesaplanır; gerekirse son adım kısalır. Yuvarlama nedeniyle yinelenen son örnek üretilmez. Adım sayısı önceden hesaplanır; 1.000.000'dan fazla örnek istenirse `ValueError` verilir. Bu sınır ürün tercihi olup ortak değiştirilebilir.
- Çözücüler aynı `t` dizisini alır; `t` en az iki örnektir, bir boyutlu, sonlu ve kesin artandır. `y0` ve `v0`, `t[0]` anındaki başlangıç koşullarıdır. Analitik çözümde `tau=t-t[0]` kullanılır.
- Response içindeki `t`, `y`, `v` şekli `(N,)` ve uzunlukları eşittir. Girdileri yerinde değiştirme; çıktılar girdi dizilerini paylaşmasın. `method` yalnız `analytical`, `euler`, `rk4` değerlerinden biridir.
- `classify_roots` çıktısı `distinct_real`, `repeated_real` veya `complex_conjugate` olur. Bu sadece karakteristik kök sınıfıdır; tek başına kararlılık veya lab Case numarası değildir. Ayırt edici sıfır karşılaştırmasında ölçekli tolerans kullanılır; tolerans ve kritik sınıra yakın davranış Kişi 1 tarafından belgelenir.
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

`ui/`, `__main__.py`, `tests/ui/`, `tests/integration/` ve README senin alanındır. Parametre girişi, controller, hata mesajları ve Qt canvas yerleştirmesini geliştir. Çözücü veya grafik hesabını UI içinde yeniden yazma.

**İş yükü: 16 göreli puan.** İskelet 3, girişler 3, seçim/grafik bağlantısı 4, entegrasyon 4, dokümantasyon/review 2. Entegrasyon emeği bu rolün iş yüküne dahildir; görsel süsleme ve ek özellikler öncelikli değildir.

## 7. Adım adım geliştirme

### M1 — Ekran iskeleti (3 puan)
1. Tek ana pencere: model parametreleri, simülasyon ayarları, yöntem seçimleri, çalıştır butonu, grafik alanı, hata metrikleri ve durum alanı tasarla.
2. `python -m dss` girişini ve QApplication yaşam döngüsünü düzenle.
3. Grafik alanında etiketli örnek veri kullan; Kişi 4 hazır değilse yalnız test double'ı ile çalış. Gerçek çözücü çıktılarını bekleme.
4. UI state'ini widget kodundan ayır; controller saf hesaplamaya erişsin, pencere sonuçları sunsun.

**Kabul:** Pencere açılır ve kapanır; hesaplama modülleri olmadan ekran akışı gösterilebilir.

### M2 — Giriş ve doğrulama (3 puan)
1. `a2,a1,a0,u0,y0,v0,t0,t_end,dt` alanlarını doğru etiketlerle oluştur.
2. Sayı ayrıştırma politikasını açıkça seç: nokta/virgül davranışını test et; geçersiz metni sıfır kabul etme.
3. Model/config doğrulamasını ortak fonksiyonlara bırak; kullanıcıya alanla ilişkili anlaşılır hata göster.
4. Örnek sınırı, negatif/sıfır dt, ters zaman aralığı ve boş giriş akışlarını test et.

**Kabul:** Hatalı giriş çökme veya sessiz parametre düzeltmesine yol açmaz; önceki grafik güncel sonuçmuş gibi kalmaz.

### M3 — Seçimler ve görselleştirme bağlantısı (4 puan)
1. Analitik, Euler ve RK4 seçimini ekle; boş seçim reddedilsin.
2. Üç lab Case'i ancak yönerge eşleştirmesi tamamlanınca preset yap. Öncesinde “Genel model” veya açık “Doğrulanmamış örnek” kullan.
3. Kişi 4'ün Figure nesnesini `FigureCanvasQTAgg` ile yerleştir. Tekrar çalıştırmada eski canvas/bağlantıları temizle; üst üste ekleme.
4. Hata metriklerini yalnız analitik referans seçili ve başarılıysa göster. Referans yokken “Hesaplanmadı” yaz; 0 hata gösterme.
5. Dışa aktarmada dosya seçimi, uzantı ve üzerine yazma onayını yönet; iptali hata sayma.

**Kabul:** Yöntem seçimi grafik, legend ve hata tablosuna tutarlı yansır; demo gerçek veriyle karıştırılmaz.

### M4 — Controller ve gerçek entegrasyon (4 puan)
1. `run_simulation` içinde bir kez zaman ızgarası oluştur; seçili çözücüleri aynı ızgarayla çağır.
2. Matematik hatalarını anlaşılır UI mesajına çevir; teknik ayrıntıyı debug kaydında tut. Eksik sonuçla başarı bildirme.
3. Büyük hesap UI'ı donduruyorsa hesaplamayı worker'a taşı; Qt widget'larını ana thread dışında güncelleme. Çalışma sırasında ikinci isteği engelle; eski sonuçların yeni parametrelerle etiketlenmesini önle.
4. Headless testte model/config aktarımı, yöntem sırası, hata aktarımı ve tekrar çalıştırmayı doğrula. Gerçek çözücülerle bir uçtan uca test yap.
5. Gerçek masaüstünde açılış, geçersiz giriş, yöntem değiştirme, tekrar çalıştırma, dışa aktarma ve kapanışı kontrol et. Headless başarısını bu kontrolün yerine koyma.

**Kabul:** Gerçek parametre → ortak veri → hesaplama → Figure → dışa aktarma akışı çalışır; test double'ları üretim yolundan çıkarılmıştır.

### M5 — Kullanım ve savunma (2 puan)
README'ye kurulum, çalıştırma, test ve bir kullanım senaryosu ekle. `docs/modules/ui.md` içine controller akışını ve manuel test kaydını yaz. Ortak rapora ekran akışı ve yönerge doğrulanınca gerekli ekran görüntülerini ver. Kişi 1'in PR'ını incele.

**Savunma soruları:** Doğrulama hangi katmanda? Neden controller ayrı? Bütün yöntemler neden aynı zamanı kullanıyor? Worker sonuçları pencereye nasıl güvenle aktarılıyor?

## 8. Tamamlanma ve ilk görev

- [ ] Arayüz ve giriş doğrulaması çalışıyor.
- [ ] Gerçek üç yöntem ve Figure entegrasyonu tamam.
- [ ] Hata, boş seçim, tekrar çalıştırma ve dosya iptal akışları kontrol edildi.
- [ ] Masaüstü testi, kurulum rehberi ve rapor katkısı hazır.

Örnek commitler: `feat(ui): add simulation parameter form`, `feat(ui): connect shared solver controller`, `test(ui): verify invalid input feedback`.

**Ajana ilk görev:** M1 ekran akışı ile başla; mevcut yapıyı incele ve hesaplama katmanını taklit eden açık örnek verilerle arayüz iskeleti kur. Yönergeyi görmeden Case adları ve parametreleri icat etme.
