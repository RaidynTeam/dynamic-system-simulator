# Analitik rol — M5 teslim kaydı

Kaynak taban: main `e5e9187`, 19 Ekim 2026. Rol: Kişi 1 (kullanıcının
bu konuşmada seçtiği analitik rol). Öğrenci numarası ve kapak bilgileri ortak
raporu birleştirirken kullanıcı tarafından tamamlanacaktır; burada uydurulmadı.

## Hazır teslimler

- [x] Ortak API v0.2, model doğrulaması ve üç Case sınıflandırması.
- [x] Üç Case için y(t), v(t), küçük zaman ve kritik sınıra yakın değerlendirme.
- [x] Bağımsız analitik doğruluk kontrolleri; M4 Euler/RK4 karşılaştırması.
- [x] [İngilizce rapor katkısı](../report/analytical-report.md): görev, model,
  üç türetim, kararlılık, fonksiyonlar, hassasiyet, deney yorumu ve sonuç.
- [x] [Türkçe savunma rehberi](analytical-defense-tr.md): kısa anlatım, tahtada
  Case 2 türetimi, soru-cevap ve öğrencinin çözmesi gereken alıştırmalar.
- [x] [Teknik modül açıklaması](analytical.md) ve
  [M4 ölçüm kaydı](../evidence/analytical-m4-verification.txt).
- [x] Kişi 2'nin numerical PR #10 kapsamındaki koduna yerel teknik inceleme.
- [ ] Öğrencinin kendi sözleriyle sözlü prova ve anlama değerlendirmesi.

Bu M5 teknik dokümantasyon teslimidir; öğrencinin savunmayı yaptığı veya
bütün ekip uygulamasının tamamlandığı anlamına gelmez.

## Numerical PR incelemesi

İncelenen PR: https://github.com/RaidynTeam/dynamic-system-simulator/pull/10
Merge commit: `2b51883`. Kayıt güncel main `e5e9187` üzerindeki ilgili kodun
okunması ve yerel doğrulamasıyla hazırlandı. Bu kayıt GitHub'da gönderilmiş
bir onay veya bir ekip üyesinin yaptığı insan incelemesi olarak sunulmaz.

| Kontrol | İnceleme sonucu |
|---|---|
| Denklem | Ortak RHS `[v, b0-a1*v-a0*y]`, analitik modelle aynı |
| Euler güncellemesi | y ve v aynı eski durum vektöründen güncelleniyor |
| RK4 alt aşamaları | Dört aşama her iki durum bileşenini birlikte ilerletiyor; h bir kez son ağırlıkla çarpılıyor |
| Zaman dizisi | Tam adımlar ve gerekirse kısa son adım; her çözücü gerçek interval h kullanıyor |
| Sözleşme | Float64 Response, doğru yöntem etiketi, sıfır başlangıç ve girdi belleğinden bağımsız çıktı |
| Hata davranışı | Geçersiz giriş reddediliyor; taşma açık hata; kararsız ama sonlu değerler gizlice düzeltilmiyor |
| Bağımsız kanıt | Elle ilk adımlar, doğrudan formüller, düzensiz ızgara, yakınsama ve kararlılık testleri mevcut |

İncelenen yollar içinde engelleyici bir matematik/API sorunu tespit edilmedi.
Bu sınırlı teknik inceleme tüm olası katsayıları kapsayan bir ispat değildir.

## Ortak rapora yerleştirme

1. analytical-report.md içindeki görev ve modeli ortak gereksinim/tasarım bölümüne ekleyin.
2. Üç türetimi modelin teorik açıklamasına, API tablosunu uygulama bölümüne taşıyın.
3. M4 sayısal tablo/yorumu numerical-report.md ile aynı deneylerdir; ortak raporda
   bir kez verin ve iki kişinin katkısını iş dağılımında doğru belirtin.
4. Sonuç paragrafını diğer modüllerin doğrulanmış durumu ile birleştirin.
5. Gerçek uygulama ekran görüntüleri, kapak ve ekip bilgileri ayrıca eklenmeli.

## Kalan ekip işleri

Güncel kontrol tabanında controller gerçek çözücüleri ortak ızgarada çağırıyor.
README, Run-to-plot/worker bağlantısını M4B olarak beklemede gösteriyor;
visualization modülleri henüz tamamlanmış değil. Bu nedenle boş grafik veya
test double'ı raporda gerçek uygulama kanıtı olarak kullanılmayacak.

- [ ] Gerçek görselleştirme ve Run-to-plot entegrasyonu.
- [ ] Üç Case için başlangıç/iyileştirilmiş adımlarla 5-6 gerçek uygulama görüntüsü.
- [ ] Ortak rapor, çıktı, çalıştırılabilir teslim ve RAR paketinin hazırlanması.
- [ ] Dört kişinin sözlü savunma provası.

Yeniden kontrol komutları ve M5 doğrulama sonucu
`docs/evidence/analytical-m5-verification.txt` içindedir.
