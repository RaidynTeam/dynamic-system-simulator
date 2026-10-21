# Görselleştirme rolü — Türkçe savunma rehberi

Bu dosya sözlü savunma içindir. Rapor İngilizce
(`docs/report/visualization-report.md`); burada aynı içeriği Türkçe anlatıyorsun.

## İki dakikalık anlatım

> Benim işim üç çözümü karşılaştırılabilir hâle getirmek. Kişi 1 analitik
> çözümü, Kişi 2 Euler ve RK4'ü üretiyor; ben bunları tek grafikte çiziyorum,
> aralarındaki farkı sayıyla ölçüyorum ve çıktıyı PNG/PDF olarak dışa
> aktarıyorum.
>
> Hoca "karşılaştırmalı grafik" istiyor ama bir grafiğin karşılaştırma
> yapabilmesi için iki şey gerekiyor: eğrilerin birbirinden ayırt edilebilmesi
> ve farkın bir sayıyla ifade edilmesi. İkisi de yönergede tanımlı değil,
> benim kararım.
>
> Ayırt etme için her yöntemin kendi rengi, çizgi deseni, kalınlığı ve
> işaretçisi var — sadece renge güvenmiyorum, çünkü renk körlüğü ve siyah-beyaz
> baskı ihtimali var. Referans eğriyi en kalın çiziyorum, çünkü RK4 analitik
> çözümle neredeyse çakışıyor; eşit kalınlıkta olsalar referans tamamen
> kaybolurdu.
>
> Ölçme için iki metrik veriyorum: maksimum mutlak hata ve RMSE. İkisi farklı
> soruları cevaplıyor — biri en kötü tek örneği, diğeri genel uyumu.
>
> Sonuç şu: adımı yarıya indirince Euler'in hatası 2 kat, RK4'ünki 16 kat
> azalıyor. Bu, Euler'in birinci, RK4'ün dördüncü mertebe olmasının deneysel
> karşılığı — 2¹ ve 2⁴. Bu oranları ölçtüm, teoriden türetmedim.

## Tahtada göstereceğin örnek

Rehberin elle hesaplanabilir örneği. Tahtaya yaz:

```
referans  y = [0, 1, 2]
aday      y = [0, 2, 0]
```

Mutlak fark: `|0-0| = 0`, `|2-1| = 1`, `|0-2| = 2` → `[0, 1, 2]`

- **max_abs** = 2
- **RMSE** = √((0² + 1² + 2²) / 3) = √(5/3) ≈ **1.2910**

Kodun verdiği sonuç: `max_abs = 2.0`, `rmse = 1.2909944487358056`. Birebir.

RMSE'nin max'tan küçük olduğuna dikkat çek: kök ortalama kare, en büyük değerle
sınırlı olan sayıların ortalamasıdır, onu aşamaz.

## Beklenen sorular ve kısa cevaplar

**RMSE ile maksimum hata arasındaki fark nedir?**

Maksimum hata **en kötü tek örneği** söyler. RMSE **tüm aralıktaki tipik
sapmayı** söyler. İkisi farklı soruları cevaplar: tek bir görünür sapma bile
kabul edilemezse maksimuma bakarsın, genel uyum soruluyorsa RMSE'ye.

Somut örnek: Case 1'de başlangıç adımıyla Euler için max = 0.4246, RMSE =
0.1540. En kötü örnek tipik olanın 2.76 katı. Çünkü Euler'in hatası aşım
bölgesinde yoğunlaşıyor, sonra sönüyor. Tek metrik verseydim bu bilgi kaybolurdu.

**Neden iki eğrinin aynı zaman örneklerinde olması gerekiyor?**

Çünkü hata, aynı `t` değerindeki iki `y` değerinin farkıdır. Izgaralar farklıysa
bir eğriyi diğerinin zaman noktalarına **interpolate etmem** gerekir — yani iki
çözücünün de üretmediği değerler uydururum ve ölçtüğüm şey artık yöntemlerin
hatası değil, benim interpolasyonumun hatasıyla karışmış bir şey olur.

Bu yüzden kod ızgaraları `np.array_equal` ile karşılaştırıyor ve farklıysa
sessizce yeniden örneklemek yerine **hata veriyor**. Zaten mimaride de
`make_time_grid` bir kez çağrılıp aynı dizi üç çözücüye birden veriliyor.

**Referans sıfırken yüzde hata neden sorunlu?**

Yüzde hata `|aday − referans| / |referans|` demek. Bizim sistemde `y(0) = 0`,
yani ilk örnekte payda sıfır — tanımsız. Hemen sonrasında da `y` çok küçük
olduğu için yüzde hata patlıyor: mutlak olarak önemsiz bir sapma, yüzde olarak
devasa görünüyor.

Bu yüzden sözleşme yüzde hatayı varsayılan yapmıyor. Mutlak hata bu problemde
anlamlı, çünkü `y`'nin oturduğu değer `b0/a0 = 1` ve mutlak hatayı doğrudan
yorumlayabiliyoruz.

**Küçük dt sonuçları hangi koşullarda iyileştirir?**

Yöntem kararlıysa ve yuvarlama hatası henüz baskın değilse. Bizim ölçümümüzde
beş yarılama boyunca iyileşme sürdü ve oranlar teorik değerlere **yakınsadı**:
Euler 2.71 → 2.03, RK4 17.25 → 16.09. İlk seviyelerde sapma var çünkü yüksek
mertebeli terimler hâlâ katkı yapıyor.

Ama bu sonsuza kadar gitmez. Adım küçüldükçe adım sayısı artar, her adımda
yuvarlama hatası birikir, ve bir noktadan sonra toplam hata **artmaya** başlar.
Biz o noktaya gelmedik — en küçük adımda RK4 hatası 1e-9 mertebesinde, float64
epsilon'u 2.2e-16, yani hâlâ bolca pay var.

İkinci koşul kararlılık: Euler açık bir yöntem ve büyük adımda kararsızlaşabilir.
Bizim üç Case'imizde katsayılar pozitif, sistem kararlı, bu sorun çıkmadı.

**Neden pyplot kullanmadın?**

`pyplot` her figürü global bir yöneticide tutar — uzun oturumda figürler
birikir, `close` unutulursa sızıntı olur. Ayrıca import edildiği anda bir
arayüz backend'i seçmeye çalışır, bu da PySide6'nın zaten kurduğu Qt backend'iyle
çakışır. Bunun yerine `matplotlib.figure.Figure`'ı doğrudan kullandım: global
kayıt yok, backend seçimi yok. Bir alt süreç testi figür kurulduktan sonra
`sys.modules` içinde ne pyplot ne Qt bulunduğunu kanıtlıyor.

**Metriklerin doğru olduğunu nereden biliyorsun?**

İki bağımsız kaynakla. Birincisi rehberdeki elle hesaplanan örnek — birebir
tutuyor. İkincisi daha güçlü: Kişi 2 altı senaryonun maksimum hatalarını **kendi
betiğiyle** ölçmüş, `numerical-handoff.md` içinde kayıtlı. Benim `compute_error`
aynı senaryolarda **altısında da yazılan her basamağa kadar aynı** sonucu
veriyor. İki kişi, iki ayrı kod yolu, aynı sayılar.

**Log ekseninde sıfır hatayı ne yapıyorsun?**

Log ekseni sıfır gösteremez. İlk örnekte hata her zaman tam sıfır, çünkü bütün
çözücüler aynı `y(0) = 0` koşulundan başlıyor. O örnekleri **maskeliyorum** —
eğri orada kesiliyor. Uydurma bir taban değeri koymuyorum ve eksende olmayan
bir noktaya doğru çizgi çizmiyorum. Sıfırlar verinin içinde duruyor, sadece
resimde yok. Varsayılan eksen zaten doğrusal; log isteğe bağlı.

**Demo veri neden var, gerçek sonuç mu?**

Hayır, kesinlikle değil. Ortak sözleşme `make_demo_responses` istiyor, o yüzden
var. Ama **üretim kodu onu import etmiyor** — üç gerçek çözücü hazır olduğu için
arayüzün ihtiyacı yok. Eğri de kasten yönergenin üç kapalı form çözümünden biri
değil, rasyonel bir doyum eğrisi; hem Kişi 1'in formüllerinin ikinci kopyası
olmasın hem de yanlışlıkla gerçek sonuç sanılmasın diye.

## Zayıf noktalar — sorulursa dürüst ol

- **Koyu tema eğri renkleri henüz ekip onayı almadı.** Ölçtüm: anlaşılan
  renkler koyu kartta 3:1 kontrast eşiğinin altında kalıyor, o yüzden ikisini
  açmayı önerdim. Euler'in kimliğine dokunmadım. Karar Kişi 3'te.
- **Deney tablosunu Kişi 2 ile birlikte hazırlamam isteniyordu**, ölçümlerim
  onun tablosuyla örtüşüyor ama resmî onayını almadım.
- **Rapordaki ekran görüntüleri henüz gerçek uygulamadan alınmadı**; Kişi 3'ün
  M4B-2 entegrasyonuna bağlı.
- **Çözücülerin kendi doğruluğunu ben savunmuyorum** — o Kişi 1 ve Kişi 2'nin
  alanı. Ben onların çıktısını doğru çizdiğimi ve doğru ölçtüğümü savunuyorum.

## Prova alıştırmaları

1. Tahtaya `[0,1,2]` / `[0,2,0]` örneğini yaz, max ve RMSE'yi hesapla, sonucu
   koddan oku. Süre: 2 dakika.
2. Uygulamayı aç, Case 1'i seç, başlangıç adımıyla çalıştır, Euler'in aşımını
   göster. Sonra adımı 32'ye böl, üç eğrinin çakıştığını göster.
3. Hata grafiğini doğrusal eksende göster — RK4 sıfırda yatıyor. Log eksene
   geç — üç mertebe fark ortaya çıkıyor. Neden iki eksen de gerekli, anlat.
4. "Neden aynı ızgara?" sorusuna interpolasyon argümanıyla cevap ver, 30 saniye.
