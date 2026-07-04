# Dokumentasi Historis Integrasi Midtrans & Sistem Lisensi Premium OmniGet

> [!NOTE]  
> Dokumentasi ini diarsipkan sebagai referensi historis pengembangan. Berdasarkan keputusan terbaru, semua fitur pembayaran, verifikasi lisensi, dan database lisensi telah **dihapus sepenuhnya** dari aplikasi untuk menyediakannya secara **100% gratis** bagi seluruh pengguna di dunia.

---

## 🛠️ Alur Sistem Sebelumnya

Berikut adalah alur sistem otentikasi lisensi dan gerbang pembayaran Midtrans yang sempat diimplementasikan:

```mermaid
sequenceDiagram
    actor User as Pengguna
    participant Web as Frontend Browser
    participant API as Backend Flask
    participant DB as Database SQLite
    participant Midtrans as Midtrans Snap

    User->>Web: Buka Aplikasi
    Web->>API: Periksa Cookie Lisensi
    alt Tidak Ada Cookie / Lisensi Kadaluarsa
        API->>Web: Redirect ke /activate
        User->>Web: Masukkan Email & Klik Bayar
        Web->>API: POST /api/license/buy
        API->>Midtrans: Request Snap Token
        Midtrans-->>API: Kirim Snap Token & Redirect URL
        API->>DB: Buat Transaksi Pending & Lisensi Inaktif
        API-->>Web: Kirim Token & Order ID
        Web->>Midtrans: Tampilkan Popup Pembayaran (Snap JS)
        User->>Midtrans: Lakukan Pembayaran (e.g. QRIS/OVO)
        Midtrans->>API: HTTP Webhook /api/payment/webhook
        API->>DB: Update Transaksi & Aktifkan Lisensi
        Web->>API: Poll Status /api/license/status/<order_id>
        API-->>Web: Lisensi Aktif!
        Web->>User: Tampilkan Lisensi & Simpan di Cookie
        Web->>Web: Redirect ke Beranda Downloader
    else Lisensi Valid & Aktif
        API-->>Web: Berikan Akses Penuh
    end
```

---

## ⚙️ Ringkasan Komponen yang Sempat Digunakan
1. **Database SQLite (`licenses.db`)**: Menyimpan data order, status transaksi (pending/success/expire), dan masa aktif lisensi.
2. **Midtrans Snap API**: Digunakan untuk pembuatan transaksi pembayaran dan menangani webhook notifikasi pembayaran dari server Midtrans.
3. **Middleware Lisensi**: Middleware Flask `before_request` memverifikasi keberadaan cookie lisensi aktif pada setiap rute dinamis sebelum memberikan akses.
4. **CLI Generator**: `generate_license.py` digunakan oleh pengelola sistem untuk membuat kunci lisensi manual secara offline.
