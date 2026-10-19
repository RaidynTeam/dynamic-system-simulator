# Analitik rol — Türkçe savunma rehberi

Bu belge prova içindir. Okumuş olmak veya testlerin geçmesi, öğrencinin konuyu
sözlü olarak açıklayabildiğinin değerlendirilmesi anlamına gelmez.

## İki dakikalık anlatım

“Ben ortak modelin veri yapılarını, parametre doğrulamasını, kök sınıflandırmasını
ve üç Case'in analitik çözümünü geliştirdim. Modelimiz
`y''+a1*y'+a0*y=b0*x(t)`. Giriş t=0'da 0'dan 1'e geçiyor; sistem başlangıçta
y=0 ve y'=0 durumunda. Bu yüzden t>=0 için sağ taraf b0 oluyor.

Önce sabit özel çözümü b0/a0 bulduk. Sonra homojen denklemin köklerine baktık.
Karmaşık kökler sönümlü salınım, tekrarlı kök kritik sönüm, iki farklı gerçek
kök aşırı sönüm veriyor. Başlangıç koşulları her çözümdeki iki sabiti belirliyor.
Aynı fonksiyon y(t) ve türevi v(t)'yi ortak Response biçiminde döndürüyor.

Formüllerin bilgisayardaki hesabında küçük sayı farklarından doğan hassasiyet
kaybına dikkat ettik. Kritik sınıra yakın sınıflandırma için ölçekli tolerans,
küçük zamanlarda seri açılımı kullandık. Beklenen değerleri bağımsız yüksek
hassasiyetli hesaplarla kontrol ettik. Sonra Euler ve RK4'ü aynı zamanlarda
analitik çözümle karşılaştırdık. Adım küçüldükçe hatalar azaldı ve bu örneklerde
RK4 aynı adımda daha küçük hata verdi.”

Bu metni ezberlemek yerine kendi kelimelerinle ve aşağıdaki örnekle anlat.

## Tahtada göstereceğin örnek: Case 2

1. `a1=2,a0=1,b0=1`: denklem `y''+2y'+y=1` olur.
2. Özel çözüm `K=1`. Homojen denklem `(s+1)^2=0` verir.
3. Genel çözüm `y=1+(C1+C2*t)*exp(-t)`.
4. `y(0)=0` → `C1=-1`.
5. Türev: `v=[C2-C1-C2*t]*exp(-t)`.
6. `v(0)=0` → `C2=C1=-1`.
7. Sonuç `y=1-(1+t)*exp(-t)`, `v=t*exp(-t)`.
8. t=0'da ikisi de sıfırdır. t büyürken üstel terimler sıfıra gider, y→1, v→0.
9. t=1 için `y=1-2/e≈0.2642411`, `v=1/e≈0.3678794`.

## Beklenen sorular ve kısa cevaplar

**Neden özel çözümü ayırıyorsun?**
Sabit girişin oluşturduğu dengeyi ve başlangıçtan dengeye geçişi ayırmak için.
Lineer denklemde özel ve homojen çözümlerin toplamı tam çözümdür.

**Neden iki başlangıç koşulu gerekiyor?**
Denklem ikinci dereceden; genel çözümde iki bağımsız sabit var. y(0) ve v(0)
bunları belirliyor.

**Case'i nasıl seçiyorsun?**
D=a1²-4*a0 işaretine göre. Negatif → Case 1, sıfır → Case 2, pozitif → Case 3.
Kodda doğrudan büyük kareler yerine ölçeklenmiş eşdeğer ifadeyi kullanıyoruz.

**Tekrarlı kökte neden t çarpanı var?**
İki aynı exp(s*t) terimi iki bağımsız çözüm vermez. İkinci bağımsız çözüm
`t*exp(s*t)` olur; iki başlangıç koşulunu karşılayabiliriz.

**Neden b0/a0'a yaklaşıyor?**
Kararlı dengede türevler sıfırdır; a0*y=b0 kalır. Köklerin gerçek kısımları
negatif olduğu için geçici terimler söner. Tekrarlı kökte t*exp(-sigma*t) de söner.

**b0 Case'i değiştirir mi?**
Hayır. Kök denkleminde b0 yoktur; yalnız çıktı genliğini ölçekler.

**Sınıflandırma ve kararlılık aynı şey mi?**
Sınıflandırma köklerin biçimini, kararlılık gerçek kısımlarının işaretini söyler.
Bu labda a1,a0 pozitif olduğundan üç sınıf da kararlıdır. Büyük Euler adımı
kararlı fiziksel modelin sayısal yaklaşımını yine de kararsız yapabilir.

**Analitik çözüm de hata yapar mı?**
Formül matematiksel olarak tamdır; float64 değerlendirmesi yuvarlama hatası
üretebilir. Bu yüzden “tam çözüm” bilgisayarda sonsuz hassasiyet demek değildir.

**Kritik eşitliği neden doğrudan ==0 ile kontrol etmiyorsun?**
Kayan nokta işlemlerinde yuvarlama olabilir. Normalize ayırt edicide
64*epsilon bandını kritik kabul ediyoruz. Bu bir uygulama tercihi ve çok yakın
modeller için tekrarlı kök yaklaşımıdır; bütün modellerin tam olarak kritik
olduğu iddia edilmez.

**sinc ve expm1 ne işe yarıyor?**
Sinüsün küçük argümanda argümana bölünmesini ve exp(x)-1 farkını daha güvenli
hesaplıyorlar. NumPy sinc(x)=sin(pi*x)/(pi*x) tanımını kullanır.

**Neden küçük t için seri var? Bu sayısal çözüm mü?**
Yakın iki sayıyı çıkarırken gerçek küçük çıktı kaybolabiliyor. Aynı analitik
modelin t=0 çevresindeki açılımını değerlendiriyoruz. Önceki örnekten adımlayarak
integrasyon yapmıyoruz; Euler/RK4 yerine geçen ikinci bir çözücü yazmadık.

**Aynı zaman dizisi neden zorunlu?**
Farklı anlardaki değerleri çıkarmak yalnız yöntem hatasını ölçmez. Controller
bir kez ızgara üretiyor ve seçilen bütün çözücülere aynı t dizisini veriyor.

**RK4 her zaman yeterince doğru mu?**
Hayır. M4 Case 3'te başlangıç adımında RK4 maksimum hatası yaklaşık 0.01335'ti;
seçtiğimiz 0.01 hedefini aştı. Uygun adım yine gerekiyor.

**0.01 hedefini hoca mı verdi?**
Hayır. b0=a0=1, t_end=20 örnekleri için ekip ölçütü. PDF başlangıç adımını ve
uyuşmazlıkta adımı yarılamayı istiyor; sayısal tolerans belirtmiyor.

**Testler nasıl bağımsız?**
Üç Case için yüksek hassasiyetli Decimal referansları, başlangıç/limit kontrolleri,
türev tutarlılığı ve ODE artığı var. Analitik beklenen değerleri Euler/RK4'ten
kopyalamıyoruz. Numerical karşılaştırma, bağımsız analitik doğrulamanın sonrasında.

## Prova alıştırmaları

- a1=1,a0=1,b0=1 için Case'i, son değeri ve salınım beklentisini söyle.
- a1=2,a0=1,b0=2 için Case 2 formülünü yaz; y(0), v(0) ve limiti kontrol et.
- a1=3,a0=1,b0=1 için köklerin ikisinin de negatif olduğunu göster.
- b0 iki katına çıkarsa y ve v'nin ne olacağını gerekçelendir.
- Hocanın 1 saniye örneğinde Euler hata oranını sorarsa: bu özel modelde
  önde gelen hata terimi o noktada sıfırlanabiliyor; yakınsama için M4'te t=2 seçildi.
- Kendi kodunda solve_analytical, classify_case ve Response veri akışını açıp anlat.

Her alıştırmada önce kendin cevap ver; sonra rapordaki türetimle karşılaştır.
Gerçek sözlü prova ve anlama değerlendirmesi henüz yapılmadı.
