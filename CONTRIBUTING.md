# Katkı süreci

Bu dosya ekibin üzerinde anlaştığı Git ve PR kurallarını toplar. Kurallar
`docs/team/ORTAK-SOZLESME-v0.2.md` ile aynıdır; burada günlük kullanım için
derli toplu hâlde duruyor.

**Bu kuralların GitHub üzerinde teknik olarak zorunlu kılındığı varsayılmaz.**
Depoda branch protection açık değildir; kurallar ekip disiplinine dayanır.

## Başlamadan önce

Kendi rol belgenizi `docs/team/` altında okuyun. `AGENTS.md` ve ortak sözleşme
de bağlayıcıdır. Kurulum ve çalıştırma komutları `README.md` içindedir.

## Branch

- `main` teslime hazır sürümdür. **Doğrudan `main`'e push yapılmaz.**
- Her milestone için güncel `main`'den küçük bir branch açın:
  `feat/<scope>-m1`, `feat/<scope>-m2` gibi.
- Bir branch merge olduktan sonra bir sonrakini **güncel `main` üzerinden**
  açın. Uzun ömürlü tek branch zorunlu değildir.
- **Force push yapılmaz.** Zorunlu bir durum varsa (ör. yanlış yazar bilgisini
  düzeltmek) önce ekibe haber verin, yalnız kendi branch'inizde ve
  `--force-with-lease` ile yapın, sebebini PR açıklamasına yazın.
- Başkasının branch'ini veya çalışmasını silmeyin.

## Commit

Biçim: `<type>(<scope>): <English imperative description>`

Örnek: `feat(numerical): implement euler integration`

| | |
|---|---|
| **Türler** | `feat`, `fix`, `test`, `docs`, `refactor`, `chore`, `ci` |
| **Scope'lar** | `analytical`, `contracts`, `numerical`, `ui`, `plot`, `analysis`, `project` |

- Her commit **tek mantıksal değişikliktir**. Kod ve onun testi birlikte
  gidebilir; ilgisiz iki düzeltme ayrı commit olur.
- Açıklama İngilizce ve emir kipindedir.
- Listede olmayan bir tür kullanmayın.

**Commit'e asla girmeyecekler:**

- `.venv/`, `__pycache__/`, derleme çıktıları (hepsi `.gitignore`'da)
- `.env`, erişim anahtarı, token, parola
- Uydurma test çıktısı veya ölçülmemiş deney sayısı
- Başka bir kişiye ait yazar bilgisi

## Pull request

PR açıklamasında şunlar bulunur:

1. **Amaç ve sonuç** — hangi sorun, ortaya çıkan davranış ne
2. **Değişiklikler** — hangi dosya, ne yapıyor
3. **Testler ve gerçek sonuçlar** — çalıştırılan komut ve **gerçek çıktı**
4. **Eksikler / API etkisi** — ortak sözleşmede değişen bir şey var mı
5. **İlgili görev** — milestone; Issue numarası yoksa **uydurmayın**, görev
   başlığını yazın

Çalıştırılmamış bir test "çalıştırıldı" diye yazılmaz. Çalıştırılamadıysa
"çalıştırılmadı" olarak belirtilir.

PR açıklaması Markdown'dır. Bir dosyadan kopyalıyorsanız **ham kaynaktan**
kopyalayın; önizleme görünümünden kopyalarsanız başlıklar ve tablolar kaybolur.

## Review

Review halkası — ok **inceleyen → PR sahibi** demektir:

```
Kişi 1 → Kişi 2 → Kişi 4 → Kişi 3 → Kişi 1
```

- Merge PR üzerinden ve **en az bir başka ekip üyesinin incelemesiyle** olur.
- Testler geçmeden birleştirilmez.
- Halkadaki kişi müsait değilse **başka bir üye inceleyebilir**; zorunlu olan
  "en az bir başka kişi" şartıdır, halka yalnız varsayılan atamadır. Sapma
  olduğunda sebebini PR'a yazın ki kayıt dışı kalmasın.
- Onayı GitHub'ın **Review** mekanizmasıyla verin. Sözlü "baktım, tamam"
  kayıtta görünmez ve rapora yazılamaz.
- Ortak sözleşmeyi değiştiren PR'ları dört kişi de görür.

**İnceleyene:** yalnız testlerin geçmesine bakmayın. Sayıların gerçekten
ölçülüp ölçülmediğini, ortak API'nin bozulup bozulmadığını ve başka kişiye ait
dosyaya dokunulup dokunulmadığını kontrol edin.

## Ortak sözleşme ve dosya sahipliği

- Her ortak dosyanın tek sahibi vardır; başkasının modülünü sessizce
  değiştirmeyin. Gerekli değişikliği gerekçe ve önerilen imzayla sahibine
  bildirin, mutabakattan sonra uygulayın.
- Ortak API (`src/dss/contracts.py` ve sözleşmedeki imzalar) **v0.2**'dir.
  İmza genişletmek gerekiyorsa sadece-anahtar-kelimeli ve varsayılanlı
  parametre tercih edin; konumsal çağrı bozulmasın.
- Matematik modülleri Qt veya Matplotlib içe aktarmaz. Bağımlılık yönü:
  `contracts → analytical/numerical/visualization → ui`.
- Başkasının modülünü kopyalayıp ikinci bir uygulama yazmayın.

## Test

Tam paket, headless:

```
$env:QT_QPA_PLATFORM = "offscreen"
.\.venv\Scripts\python.exe -m pytest -q
Remove-Item Env:QT_QPA_PLATFORM
```

POSIX: `QT_QPA_PLATFORM=offscreen python -m pytest -q`

- Grafik testlerinde Agg backend kullanılır (`MPLBACKEND=Agg`).
- CI Windows + Python 3.11 ile çalışır; **Python 3.12 kullanmayın**, PySide6
  6.12.0'ın import kancası `six.moves` üzerinde çöküyor ve uygulama açılmıyor
  (ayrıntı: `docs/modules/visualization.md`).
- Gerçek masaüstünde etkileşim testi ayrıca Kişi 3 tarafından yapılır.

## Milestone bitişi

Bir milestone şu beşi sağlanınca biter:

- [ ] Kendi kabul kriterleri sağlandı
- [ ] Testler geçti ve çıktı kaydedildi
- [ ] `docs/modules/<modul>.md` ve `docs/evidence/` güncellendi
- [ ] Ortak API uyumu incelendi
- [ ] PR gözden geçirildi

**Testlerin geçmesi lab yönergesine uygunluğu tek başına kanıtlamaz.** Grafik
üreten değişikliklerde çıktıya gözle de bakın; otomatik test bir figürün
okunabilir olup olmadığını söyleyemez.
