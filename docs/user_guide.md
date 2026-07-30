# Panduan Pengguna OmniGet

Selamat datang di **OmniGet**, platform terpadu untuk segala kebutuhan pengunduhan media Anda. Panduan ini menjelaskan cara menggunakan setiap fitur utama secara optimal.

---

## 🚀 1. Pengunduh Video & Audio (YouTube / TikTok / DLL)
Fitur ini digunakan untuk mengunduh video dan mengonversi audio dari platform populer seperti YouTube, TikTok, Instagram, Twitter/X, Facebook, dan lainnya.

### Langkah-Langkah:
1. Salin URL/tautan video dari browser atau aplikasi ponsel Anda.
2. Tempelkan tautan ke **Bilah Pencarian Global** di bagian atas halaman.
3. Klik tombol **START DOWNLOAD** (atau pilih tab **Video/Audio** dan klik **Analisis Tautan**).
4. Setelah analisis selesai, kartu detail media akan muncul:
   * **Format**: Pilih format output yang diinginkan (MP4, MKV, WebM, MP3, M4A, atau WAV).
   * **Kualitas**: Pilih resolusi (hingga 1080p Full HD) atau bitrate audio.
   * **Batas Kecepatan**: Tentukan limit bandwidth jika Anda tidak ingin mengganggu jaringan lain.
   * **Trim (Potong)**: Masukkan waktu mulai dan selesai (format `HH:MM:SS` atau detik) jika hanya ingin mengunduh bagian tertentu.
   * **Jadwalkan**: Atur tanggal dan waktu spesifik jika unduhan ingin dijalankan nanti.
5. Klik **Unduh**. Proses pengunduhan di server akan dimonitor lewat **Circular Progress Gauge** di kolom kiri dan grafik kecepatan di kolom kanan.
6. Setelah selesai, pindai **QR Code** untuk mengunduh ke ponsel, atau klik **Unduh ke PC**.

---

## 🕷️ 2. Site Media Grabber
Fitur ini berguna untuk mengekstrak dan mengunduh seluruh media (gambar, video, audio, atau dokumen) yang tersemat pada suatu halaman situs web secara massal.

### Langkah-Langkah:
1. Tempelkan URL situs web tujuan ke Bilah Pencarian Global.
2. Pilih tab **Site Grabber**, lalu klik **START DOWNLOAD** (atau **Ambil Media**).
3. OmniGet akan merayapi (*crawling*) situs web tersebut dan menyajikan seluruh tautan berkas media yang ditemukan.
4. Anda dapat menyaring berkas berdasarkan kategori (Gambar, Video, Audio, Dokumen).
5. Klik ikon unduh pada tiap file untuk mengunduhnya secara individu, atau pilih beberapa file dan klik **Unduh Terpilih secara Massal** (.zip).

---

## 🧲 3. Pengunduh Torrent (P2P)
Mendukung pengunduhan file torrent langsung menggunakan backend berkecepatan tinggi `aria2c`.

### Langkah-Langkah:
1. Buka tab **Torrent**.
2. Anda memiliki dua opsi:
   * **Melalui URL**: Tempelkan magnet link atau URL berkas `.torrent` di kolom pencarian global dan klik **START DOWNLOAD**.
   * **Unggah File**: Seret dan jatuhkan berkas `.torrent` fisik dari PC Anda ke kotak unggah.
3. Tentukan batas kecepatan unduh (opsional).
4. Klik **Mulai Download Torrent**.
5. Status seeding dan progress akan dipantau di layar secara real-time.

---

## 🔖 4. Bookmarklet OmniGet Instan
Bookmarklet adalah tombol pintas pintar yang dipasang di browser Anda agar proses analisis tautan menjadi instan tanpa perlu bolak-balik menyalin URL.

### Cara Memasang:
1. Pastikan bilah bookmark (*bookmark bar*) browser Anda aktif (Tekan `Ctrl+Shift+B` di Chrome/Firefox).
2. Seret tombol ungu **"Seret ke Bookmark"** dari bagian bawah beranda OmniGet ke bilah bookmark Anda.

### Cara Menggunakan:
1. Buka video YouTube atau TikTok yang ingin Anda unduh.
2. Klik tombol bookmarklet OmniGet di bilah bookmark Anda.
3. Browser akan membuka tab baru ke OmniGet dan langsung menganalisis video tersebut secara otomatis.
