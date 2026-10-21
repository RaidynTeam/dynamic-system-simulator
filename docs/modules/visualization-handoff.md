# Görselleştirme rolü — M5 teslim kaydı

Kontrol tabanı: main `373b1f3`, 21 Ekim 2026. Rol: Kişi 4 — grafikler, hata
analizi ve dışa aktarma. Ödev koşulları yalnız
`docs/reference/Lab1-RTS-09102026.pdf` dosyasından alınmıştır.

## Hazır teslimler

- [x] **M1** — Qt ve `pyplot` bağımlılığı olmayan Figure altyapısı; yöntem
  kimliği (renk, çizgi deseni, kalınlık, işaretçi); açık/koyu tema paletleri;
  ortak sözleşmenin istediği örnek veri. PR #15.
- [x] **M2** — `build_response_figure`: seçili yöntemlerin y(t) eğrileri, sabit
  legend sırası, işaretçi seyreltme. PR #17.
- [x] **M3** — `compute_error` ve `build_error_figure`: yalnız konum için
  maksimum mutlak hata ve RMSE; mutlak hata grafiği; isteğe bağlı log ekseni.
  PR #18.
- [x] **M4** — `export_figure`: PNG/PDF dışa aktarımı, çıktının gözle
  incelenmesi, üç Case için adım yarılama deney tablosu. PR #19.
- [x] **M5** — bu kayıt, [İngilizce rapor katkısı](../report/visualization-report.md)
  ve ekip kurallarının tamamını taşıyan [CONTRIBUTING](../../CONTRIBUTING.md).
- [x] [Teknik modül açıklaması](visualization.md): tasarım kararları, ölçümler,
  bilinen eksikler ve aşamalar arası durum kaydı.
- [x] Kanıt kayıtları: `docs/evidence/visualization-m1-tests.txt`,
  `-m1-palette.txt`, `-m2-tests.txt`, `-m3-tests.txt`, `-m4-tests.txt`,
  `-m4-experiments.md`, `-m5-record.txt`.
- [x] Dört PR'da da CI başarılı (Windows, Python 3.11).
- [ ] Kişi 3'ün M4B-2 PR'ının incelenmesi — review halkası gereği Kişi 4'ün
  görevi. Kontrol anında açık PR yoktu; yapılmış gibi işaretlenmedi.

Ölçümler çalıştırılmış betiklerin çıktısıdır. `b0 = 1` ve `t_end = 20 s` ekip
tercihidir; yönerge yalnız başlangıç adımını ve üç Case'i seçen `(a1, a0)`
çiftlerini sabitler.

## Ortak API durumu

Sözleşmedeki dört fonksiyonun tamamı main'de ve
`dss.ui.presentation.load_visualization_api()` başarıyla dönüyor.
`prepare_results` gerçek çözücülerle uçtan uca doğrulandı: üç eğrili yanıt
figürü, iki eğrili hata figürü, iki yöntem için metrik, ayrı Figure nesneleri.

| API | Modül | Durum |
|---|---|---|
| `compute_error(reference, candidate)` | `visualization.metrics` | hazır |
| `build_response_figure(responses)` | `visualization.plots` | hazır |
| `build_error_figure(reference, candidates)` | `visualization.plots` | hazır |
| `export_figure(figure, path)` | `visualization.export` | hazır |

Ortak API v0.2 değiştirilmedi. Üç imza yalnız anahtar kelimeli ve varsayılan
değerli parametrelerle genişletildi; sözleşmedeki konumsal çağrılar aynen
çalışır:

```python
build_response_figure(responses, *, theme="light", title=None)
build_error_figure(reference, candidates, *, theme="light", title=None, scale="linear")
export_figure(figure, path, *, dpi=EXPORT_DPI)
```

## Doğrulama

Tam paket main üzerinde **565 passed**; `tests/visualization` **220 test**.

| Dosya | Test | Kapsam |
|---|---:|---|
| `test_styles.py` | 24 | Yöntem kimliği, tema paletleri |
| `test_figures.py` | 20 | Figure üretimi, eksen stili, tema uygulaması |
| `test_isolation.py` | 2 | `pyplot` ve Qt içe aktarılmadığının kanıtı |
| `test_demo_data.py` | 11 | Örnek verinin sözleşme uyumu ve determinizmi |
| `test_plots.py` | 43 | Yanıt grafiği verisi, etiketleri, reddedilen girdiler |
| `test_metrics.py` | 24 | Metrik formülleri, taşma aralığı, yakınsama |
| `test_error_plots.py` | 56 | Hata grafiği, eksen ölçeği, maskeleme |
| `test_export.py` | 40 | PNG/PDF yazımı, hata yolları, canvas korunumu |

Komut: `QT_QPA_PLATFORM=offscreen MPLBACKEND=Agg python -m pytest -q`

Otomatik testler bir figürün okunabilir olduğunu kanıtlayamaz. Bunun için
`tests/visualization/preview.py` üretim fonksiyonlarını gerçek çözücü
çıktısıyla çağırıp PNG/PDF üretir. Her aşamada gözle inceleme yapıldı ve iki
gerçek kusur bu yolla yakalandı: M2'de RK4 eğrisinin referansı kapatması,
M3'te log grafiğinde sıfır örneğine doğru çizilen artık çizgi. İkisi de
düzeltildi.

Metrikler iki bağımsız kaynakla doğrulandı: rehberdeki elle hesaplanan örnek
(`max = 2`, `RMSE = √(5/3)`) ve Kişi 2'nin `numerical-handoff.md` içindeki
ölçüm tablosu. Altı senaryonun tamamında yazılan her basamak örtüşüyor.

## Diğer rollerden beklenenler

- [ ] **Kişi 3 — koyu tema eğri renkleri.** Koyu kart `#1E293B` üzerinde
  Exact `#475569` 1.93:1, RK4 `#2563EB` 2.83:1 kontrast veriyor; metin dışı
  işaretler için 3:1 eşiğinin altında. Önerilen değişiklik yalnız bu ikisini
  açmak: Exact `#CBD5E1`, RK4 `#60A5FA`. Euler `#FF1D8D` iki temada da
  korunur. Ölçümler `docs/evidence/visualization-m1-palette.txt`. Açık tema
  değerlerine dokunulmadı.
- [ ] **Kişi 3 — M4B-2 entegrasyonu.** Görselleştirme tarafında engel kalmadı.
  Öneri: `build_response_figure`'a `title` geçilsin. Sözleşme imzası
  `ModelParams` almadığı için figür a1/a0/b0 değerlerini kendisi üretemiyor;
  rapora girecek görüntülerde parametrelerin başlıkta görünmesi beklenir.
- [ ] **Kişi 3 — tek kaynak renk.** `src/dss/ui/colors.py` içindeki
  `METHOD_COLORS` aynı değerlerin ikinci kopyası. `dss.visualization.styles`
  Matplotlib içe aktarmadığı için oradan almak UI'a ek bağımlılık getirmez.
- [ ] **Kişi 2 — deney tablosu onayı.** Rehber bu deneyin Kişi 2 ile birlikte
  hazırlanmasını istiyor. Ölçümler onun tablosuyla örtüşüyor; onay alınmadı.
- [ ] **Ortak — rapor görselleri.** 5–6 ekran görüntüsü gerçek uygulamadan,
  M4B-2 sonrasında alınmalı. Senaryo önerisi Kişi 2'nin kaydındadır.
- [ ] **Ortak — raporun birleştirilmesi ve RAR teslim paketi.**

## Süreç gözlemleri ve alınan önlemler

Ekip kurallarıyla uygulama arasındaki farklar; sonraki milestone'larda
tekrarlanmaması için kayda geçirildi.

**Review kaydı.** İlk üç PR (#15, #17, #18) GitHub'da kayıtlı bir inceleme
almadan birleştirildi; ikisini PR sahibi dışında bir üye açmıştı. PR #19'dan
itibaren PR'ı sahibi açtı ve inceleyiciyi kendisi atadı; projenin ilk kayıtlı
onayı bu PR'da alındı. Alınan önlem: CONTRIBUTING, onayın GitHub'ın Review
mekanizmasıyla verilmesini şart koşuyor — sözlü onay kayıtta görünmediği için
rapora da yazılamaz.

**Review halkası.** PR #19'da halkadaki inceleyici (Kişi 2) müsait değildi;
yerine Kişi 3 inceledi ve sebep PR açıklamasına yazıldı. Kuralın bağlayıcı
kısmı olan "en az bir başka kişinin incelemesi" karşılandı. Alınan önlem:
CONTRIBUTING bu durumu açıkça düzenliyor — halka varsayılan atamadır, inceleyici
müsait değilse başka bir üye inceleyebilir ve sapmanın sebebi PR'a yazılır.

**Force push.** `feat/visualization-m1` dalında bir kez kullanıldı; amaç commit
mesajlarındaki bir ortak yazar satırını kaldırmaktı. Dal o sırada birleştirilmemişti,
açık PR'ı ve atanmış inceleyicisi yoktu, dosya içerikleri değişmedi ve komut
`--force-with-lease` ile çalıştırıldı. Ekip kuralı force push'u yasakladığı için
kaydediliyor. Alınan önlem: CONTRIBUTING, zorunlu durumda izlenecek yolu
tanımlıyor — önce ekibe haber, yalnız kendi dalında, `--force-with-lease` ile
ve sebebi PR'da belirtilerek.

**Çalışma ortamı.** Geliştirmenin başında Python 3.12 denendi; PySide6 6.12.0'ın
içe aktarma kancası `six.moves` üzerinde başarısız olduğu için uygulama hiç
açılmadı ve `tests/ui` toplanamadı. Depo kaynaklı bir sorun değildir, aynı hata
değişmemiş main'de de tekrarlanır. Python 3.11.9 kuruldu. Alınan önlem:
CONTRIBUTING ve modül belgesi 3.12'nin kullanılmamasını not ediyor.

## Durum özeti

Kişi 4'ün dört fonksiyonu, 220 testi ve rapor katkısı tamamdır. Kalan maddeler
diğer rollerin onayına veya ortak teslim adımlarına bağlıdır; bu kayıt bütün
uygulamanın veya ortak teslimin tamamlandığı anlamına gelmez. Yönergeye göre
teslim 26 Ekim 2026 Pazartesi 08.00, notlandırma %40 rapor ve %60 uygulamayı
açıklamadır.
