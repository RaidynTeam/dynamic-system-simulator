# Görselleştirme teslim kaydı

Bu kayıt Kişi 4'ün teslimini ve kalan ekip bağımlılıklarını gösterir.
Ödev koşulları yalnız `docs/reference/Lab1-RTS-09102026.pdf` dosyasından
alınmıştır. Kontrol tabanı: main `373b1f3` (21 Ekim 2026). Rapor katkısı
İngilizce; Türkçe savunma anlatımı ayrı dosyada.

## Hazır olan katkılar

- [x] **M1**: Qt ve pyplot'tan bağımsız Figure altyapısı, yöntem kimliği
  (renk + çizgi deseni + kalınlık + işaretçi), açık/koyu tema paletleri,
  sözleşmenin istediği örnek veri. PR #15.
- [x] **M2**: `build_response_figure` — seçili yöntemlerin y(t) eğrileri,
  başlık/etiket/legend/grid, işaretçi seyreltme. PR #17.
- [x] **M3**: `compute_error` ve `build_error_figure` — yalnız y için maksimum
  mutlak hata ve RMSE, mutlak hata grafiği, isteğe bağlı log ekseni. PR #18.
- [x] **M4**: `export_figure` — PNG/PDF, dışa aktarılan çıktının gözle
  incelenmesi, üç Case için adım yarılama deney tablosu. PR #19.
- [x] **M5**: bu kayıt, [İngilizce rapor katkısı](../report/visualization-report.md),
  genişletilmiş [CONTRIBUTING](../../CONTRIBUTING.md) ve sözlü savunma
  hazırlığı. Savunma notları kişisel çalışma malzemesi olduğu için depoda
  tutulmuyor.
- [x] Dört PR'da da CI (Windows, Python 3.11) başarılı.
- [x] [Teknik notlar](visualization.md): tasarım kararları, ölçümler, bilinen
  eksikler ve aşamalar arası durum kaydı.
- [x] Kanıt kayıtları: `docs/evidence/visualization-m1-tests.txt`,
  `-m1-palette.txt`, `-m2-tests.txt`, `-m3-tests.txt`, `-m4-tests.txt`,
  `-m4-experiments.md`.

Ölçümler çalıştırılmış betiklerin çıktısıdır, bu dosyanın veya rehberlerin
varsayımı değildir. `b0 = 1` ve `t_end = 20 s` ekip tercihidir; yönerge
yalnız başlangıç adımını ve üç Case'i seçen `(a1, a0)` çiftlerini sabitler.

## Ortak API durumu

Sözleşmedeki dört fonksiyonun **hepsi** main'de:

| API | Durum |
|---|---|
| `compute_error(reference, candidate)` | hazır |
| `build_response_figure(responses)` | hazır |
| `build_error_figure(reference, candidates)` | hazır |
| `export_figure(figure, path)` | hazır |

`dss.ui.presentation.load_visualization_api()` artık başarıyla dönüyor.
`prepare_results` gerçek çözücülerle uçtan uca denendi: 3 eğrili yanıt figürü,
2 eğrili hata figürü, iki yöntem için metrik, ayrı Figure nesneleri.

Ortak API v0.2 **değiştirilmedi**. Üç imza sadece-anahtar-kelimeli ve
varsayılanlı parametrelerle genişletildi; sözleşmedeki konumsal çağrılar aynen
çalışır:

```python
build_response_figure(responses, *, theme="light", title=None)
build_error_figure(reference, candidates, *, theme="light", title=None, scale="linear")
export_figure(figure, path, *, dpi=EXPORT_DPI)
```

## Testler

Tam paket main üzerinde **565 passed**. `tests/visualization` toplam **220
test**: 24 kimlik/tema, 20 figür altyapısı, 11 örnek veri, 2 izolasyon,
43 yanıt grafiği, 24 metrik, 56 hata grafiği, 40 export.

Komut: `QT_QPA_PLATFORM=offscreen MPLBACKEND=Agg python -m pytest -q`

Testler bir figürün **okunabilir** olduğunu kanıtlayamaz. Bunun için
`tests/visualization/preview.py` var; üretim fonksiyonlarını gerçek çözücü
çıktısıyla çağırıp PNG/PDF üretir. Her milestone'da gözle inceleme yapıldı ve
iki kez gerçek sorun yakalandı: RK4'ün referans eğriyi kapatması (M2) ve log
grafiğindeki hayalet dikey çizgi (M3).

## Beklediklerim

- [ ] **Kişi 3 — koyu tema eğri renkleri onayı.** Koyu kart `#1E293B` üzerinde
  Exact `#475569` 1.93:1, RK4 `#2563EB` 2.83:1 kontrast veriyor; ikisi de metin
  dışı işaretler için 3:1 eşiğinin altında. Önerim yalnız bu ikisini açmak:
  Exact `#CBD5E1`, RK4 `#60A5FA`. **Euler `#FF1D8D` iki temada da aynı.**
  Ölçümler `docs/evidence/visualization-m1-palette.txt`. Açık tema değerlerine
  dokunulmadı.
- [ ] **Kişi 3 — M4B-2 entegrasyonu.** Teknik engel kalmadı. Öneri: M4B-2'de
  `build_response_figure`'a `title` geçin; sözleşme imzası `ModelParams`
  almadığı için figür a1/a0/b0 değerlerini kendisi bilemiyor, rapora girecek
  görüntülerde parametrelerin başlıkta görünmesi işinize yarar.
- [ ] **Kişi 3 — tek kaynak renk önerisi.** `src/dss/ui/colors.py` içindeki
  `METHOD_COLORS` aynı değerlerin ikinci kopyası. `dss.visualization.styles`
  bilerek Matplotlib import etmiyor, oradan almak UI'a ek bağımlılık getirmez.
- [ ] **Kişi 2 — deney tablosu onayı.** Rehber bu deneyin onunla birlikte
  hazırlanmasını istiyor. Ölçümlerim `numerical-handoff.md` içindeki altı
  satırla her basamağına kadar örtüşüyor; resmî onay alınmadı.
- [ ] **Ortak — rapordaki 5–6 ekran görüntüsü.** Gerçek uygulamadan, M4B-2
  sonrasında alınmalı. Senaryo önerisi Kişi 2'nin kaydında.
- [ ] **Ortak — raporu birleştirme ve RAR teslim paketi.**

## Benim yapacaklarım

- [ ] **Kişi 3'ün PR'ını inceleme.** Review halkası gereği Kişi 4 → Kişi 3.
  M4B-2 PR'ı açıldığında inceleyeceğim. Kontrol anında açık PR yoktu, bu yüzden
  yapılmış gibi işaretlenmedi.

## Süreçle ilgili dürüst notlar

Bunlar ekip kurallarıyla ilgili gerçekleşen sapmalardır; kayıt dışı kalmasın
diye yazılıyor.

- **PR #15, #17 ve #18 review almadan merge edildi.** Üçünü de Kerem birleştirdi;
  #15 ve #17'yi kendisi açmıştı. Ekip kuralı "en az bir başka kişinin
  incelemesi" diyor. **PR #19 ilk kayıtlı review'u aldı** (`furkanisanci`
  onayladı), çünkü PR o kez Kişi 4 tarafından açıldı ve reviewer atandı.
- **PR #19'da review halkasından sapıldı.** Halkaya göre inceleyen Kişi 2
  olmalıydı; müsait değildi, yerine Kişi 3 inceledi. Sebep PR'a yazıldı.
  Kuralın zorunlu kısmı ("en az bir başka kişi") karşılandı.
- **Bir kez force push yapıldı.** `feat/visualization-m1` dalında, commit
  mesajlarından bir ortak-yazar satırını kaldırmak için, `--force-with-lease`
  ile ve kullanıcının açık onayıyla. Dal o anda henüz merge edilmemişti, PR'ı
  ve reviewer'ı yoktu, dosya içeriği değişmedi. Ekip kuralı force push'u
  yasaklıyor; bu yüzden kayda geçiriliyor. CONTRIBUTING'e bu durumda izlenecek
  yol eklendi.
- **Geliştirme sırasında Python 3.12 denendi ve uygulama hiç açılmadı.**
  PySide6 6.12.0'ın import kancası `six.moves` üzerinde çöküyor. Depo hatası
  değil; 3.11 kuruldu. Ayrıntı `visualization.md` içinde, uyarı CONTRIBUTING'e
  eklendi.

## Durum özeti

Kişi 4'ün dört fonksiyonu, 220 testi, rapor katkısı ve savunma hazırlığı
tamamdır. Kalan maddeler başka kişilerin onayına veya ortak teslim adımlarına
bağlıdır. **Bu, bütün uygulamanın veya ortak teslimin tamamlandığı anlamına
gelmez.** Yönergeye göre teslim 26 Ekim 2026 Pazartesi 08.00; notlandırma
%40 rapor, %60 uygulamayı açıklama.
