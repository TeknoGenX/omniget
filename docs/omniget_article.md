# OmniGet: Media Downloader Universal & P2P Client Premium yang 100% Gratis Tanpa Iklan

Di era digital saat ini, kebutuhan untuk menyimpan konten media dari internet untuk keperluan offline—mulai dari video tutorial, musik, gambar, dokumen, hingga file torrent—sangatlah tinggi. Sayangnya, sebagian besar layanan pengunduh media online saat ini dipenuhi oleh iklan pop-up yang mengganggu, pembatasan kecepatan unduh, jebakan langganan premium, bahkan ancaman malware.

Sebagai jawaban atas tantangan tersebut, hadir **OmniGet**—sebuah aplikasi web media downloader universal dan P2P torrent client berskala premium yang dirancang agar **100% gratis, bebas iklan, aman, dan dapat di-host sendiri (self-hosted)** oleh siapa saja.

---

## 💎 Desain Visual Premium: Glassmorphism Dashboard

OmniGet menepis anggapan bahwa aplikasi utilitas open-source harus berpenampilan kaku dan membosankan. Dibangun dengan konsep estetika modern **Glassmorphism**, antarmuka OmniGet memberikan visualisasi yang memukau:
* **Dark Mode Elegan**: Latar belakang gelap transparan dengan perpaduan warna aksen neon ungu-biru yang dinamis.
* **Dashboard Interaktif**: Dilengkapi dengan **Circular Progress Gauge** yang halus untuk memantau unduhan aktif.
* **Speed Monitoring Real-Time**: Grafik garis (line chart) interaktif yang melacak kecepatan lalu lintas bandwidth (Mbps) secara langsung.
* **Activity Analytics**: Statistik otomatis yang melacak jumlah dan kategori berkas yang telah Anda unduh.

---

## 🚀 Fitur-Fitur Unggulan

### 1. Pengunduh Video & Audio Universal
Didukung oleh backend parser `yt-dlp` terupdate, OmniGet mampu mengunduh video hingga kualitas 1080p Full HD dan mengekstrak audio berkualitas tinggi (MP3/M4A/WAV) dari ratusan platform populer seperti YouTube, TikTok, Instagram, Twitter/X, dan Facebook. Fitur ini juga dilengkapi dengan:
* **Presisi Trimming (FFmpeg)**: Anda dapat memotong durasi video/audio langsung sebelum diunduh hanya dengan memasukkan waktu mulai dan selesai.
* **Unduhan Terjadwal**: Memungkinkan Anda menjadwalkan pengunduhan pada waktu tertentu di latar belakang.
* **Batas Kecepatan**: Membatasi bandwidth unduhan agar tidak mengganggu koneksi pengguna lain.

### 2. Multi-threaded Segmented Downloader
Untuk berkas langsung (Direct Link seperti `.zip`, `.iso`, `.exe`), OmniGet menggunakan teknologi segmentasi multi-threaded. Berkas akan dipecah menjadi beberapa segmen yang diunduh secara bersamaan, meningkatkan kecepatan unduh hingga **4x lipat** dibandingkan unduhan browser biasa.

### 3. P2P Torrent Downloader Terintegrasi
Tidak perlu lagi menginstal aplikasi torrent client terpisah. OmniGet mengintegrasikan engine P2P berkecepatan tinggi `aria2`. Cukup tempelkan magnet link atau unggah berkas `.torrent`, dan aplikasi akan langsung mengunduh file tersebut dengan aman di latar belakang.

### 4. Site Media Grabber (Web Crawler)
Ingin mengunduh seluruh gambar atau video dari sebuah halaman web? Fitur Site Grabber akan memindai (*crawling*) situs target secara instan, menyaring berkas berdasarkan kategori (Gambar, Video, Audio, Dokumen), dan memungkinkan Anda mengunduhnya secara massal dalam format `.zip`.

### 5. Tombol Pintas Bookmarklet Pintar
Proses menyalin dan menempelkan tautan bisa menjadi sangat repetitif. OmniGet menyertakan **Bookmarklet** yang dapat Anda seret ke bilah bookmark browser Anda. Saat membuka video di YouTube atau TikTok, cukup klik bookmarklet tersebut, dan tab OmniGet akan otomatis terbuka dan menganalisis video tersebut secara instan.

---

## 🔒 Keamanan Tingkat Tinggi (Hardened Security)

Sebagai aplikasi yang berjalan di server, keamanan adalah prioritas utama. OmniGet telah melewati audit keamanan ketat dan dilengkapi proteksi industri terhadap:
* **Server-Side Request Forgery (SSRF)**: Mencegah penyerang menggunakan server untuk memindai jaringan privat internal melalui pemblokiran alamat IP lokal/loopback dan validasi status pengalihan HTTP 302.
* **Path Traversal & Argument Injection**: Validasi ketat nama berkas torrent dan parameter subtitel agar penyerang tidak bisa membaca atau menimpa berkas sistem operasi induk.
* **DOM-based XSS**: Enkoding HTML penuh pada setiap keluaran dinamis untuk mencegah eksekusi skrip berbahaya di browser pengguna.

---

## 📦 Pemasangan Mudah: Paket Debian & Docker

OmniGet dirancang agar sangat portabel dan mudah disebarluaskan:
* **Paket Debian (.deb)**: Tersedia paket instalasi mandiri untuk OS berbasis Linux (Ubuntu/Debian) yang otomatis mengonfigurasi virtual environment Python, dependensi sistem (`ffmpeg`, `aria2`), dan mendaftarkan daemon layanan latar belakang (`systemd`).
* **Deployment Hugging Face (Docker)**: Dapat dideploy secara instan di Hugging Face Spaces secara gratis selamanya dengan alokasi RAM 16 GB hanya dengan sekali klik menggunakan berkas Dockerfile yang telah dioptimalkan.

---

## 🌐 Kesimpulan & Open Source

OmniGet membuktikan bahwa performa premium, antarmuka cantik, dan fitur lengkap pengunduhan media dapat diperoleh secara **gratis tanpa iklan**. Dengan sifatnya yang open-source, privasi data Anda terjamin sepenuhnya karena seluruh berkas disimpan secara lokal di server Anda sendiri.

Kunjungi repositori rilis resmi kami untuk mengunduh paket Debian atau mempelajari dokumentasinya:
👉 **[Repositori Rilis GitHub OmniGet](https://github.com/TeknoGenX/omniget.git)**
