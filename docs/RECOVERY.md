# İşlem hatasından sonra devam etme

6.5.0, hata kodunun yanında neden ve sonraki adımı gösterir. Son başarılı rapor ve mevcut bakım ilerlemesi hata yüzünden silinmez. Bu pencerede kalan raporların uygulama yeniden açılınca otomatik geri geleceği söylenmez.

- Tamamlanamayan bilgi okuma/tarama: kullanıcı isterse yalnız aynı kontrolü yeniden çalıştırır. İstek seçenekleri ve ilgili ekran, hatanın oluştuğu andan alınır.
- Sürücü yükleme, temizlik, geri yükleme, paket uygulama ve diğer değişiklikler: otomatik veya tek düğmeli tekrar yoktur. İlgili ekrana dönüş gezinmedir; yeni sonuç ve gerekli onaylar kullanıcı tarafından incelenir.
- İptal: önceki sonuç durur; iptal başarı sayılmaz.
- Eskimiş tarama/seçim: yeni tarama ve seçim gerekir.
- İşlem motorunun açılamaması, kapanması veya bozuk yanıtı: bekleyen istekler bir kez hata ile sonuçlanır. Sonraki istekler hemen hata verir; durum sorgulaması durur. Arayüzdeki raporlar incelenebilir. Motor kendiliğinden yeniden başlatılmaz; Windows işleminin sonucu doğrulanamadıysa işlem devam ediyor olabilir.
- Hata bilgisini kopyala: uygulama sürümü, ekran adı, sabit hata kodu ve açıklama. İstek içeriği, dosya yolu veya olay günlüğü mesajları eklenmez. Panoya yerel kopyalar; bir yere göndermez.

Arayüz ve işlem motoru arasındaki protokol QProcess üzerinden sınanır: başlatılırken kuyruklanan ilk istek, açılamayan motor, beklenmeyen kapanma, bozuk yanıt, normal kapatma ve kapanma sonrası istekler. Qt geri çağırma hatası protokol hatası olarak sınıflandırılmaz.

Paketin opt-in `--smoke` testi, normal Windows taramaları ve veri koruma kontrolleri bittikten sonra yalnız kendi boşta duran Node sürecini kapatır. Gerçek paket üzerinde anında hata, duran sorgulama ve korunan rapor/ilerleme doğrulanır. Çalışan Windows kurulumunu öldürme veya kendiliğinden tekrar uygulama testi değildir. Normal başlangıç bu hata enjeksiyonunu çalıştırmaz.
