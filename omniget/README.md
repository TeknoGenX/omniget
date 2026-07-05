# OmniGet - Release & Distribution Package

Ini adalah repositori rilis dan distribusi resmi untuk **OmniGet**, media downloader universal dengan antarmuka **Glassmorphism Premium**. Repositori ini menyediakan paket instalasi Debian (`.deb`) siap pasang, dokumentasi lengkap, panduan deployment, serta panduan pengguna akhir.

---

## 🚀 Fitur Utama OmniGet

1. **Universal Video & Audio Downloader**:
   * Mengunduh video (MP4) hingga resolusi 1080p dan audio (MP3) dari YouTube, TikTok, Instagram, Twitter/X, dan lainnya menggunakan backend `yt-dlp` terupdate.
   * Integrasi pemotongan media (*ffmpeg trimming*) secara presisi sebelum berkas diunduh.
   * Batasan kecepatan (*speed limiter*) dinamis.
2. **P2P Torrent Downloader**:
   * Pengunduhan magnet link dan file `.torrent` menggunakan engine backend berkinerja tinggi `aria2`.
3. **Site Media Grabber**:
   * Menjelajahi dan mengunduh seluruh berkas gambar, video, audio, dan dokumen dari halaman website apa saja secara massal.
4. **Bookmarklet Instan**:
   * Tombol pintas sekali klik di bilah browser untuk menganalisis dan mengunduh video secara instan tanpa perlu bolak-balik menyalin tautan.
5. **Keamanan Kelas Industri (Hardened Security)**:
   * Proteksi SSRF, bypass redirect HTTP 302, XSS, Path Traversal, dan Argument Injection.

---

## 📁 Struktur Direktori Rilis

Berikut adalah susunan berkas dalam paket rilis distribusi ini:

```text
omniget/
├── README.md               # Deskripsi umum rilis (berkas ini)
├── LICENSE                 # Berkas Lisensi MIT resmi
├── CHANGELOG.md            # Riwayat perubahan & perbaikan bug versi 1.0.0
├── INSTALL.md              # Panduan pemasangan cepat (.deb)
├── screenshots/
│   └── dashboard_mockup.jpg # Tangkapan layar antarmuka premium Glassmorphism UI
├── docs/                   # Pusat Dokumentasi Lengkap
│   ├── bug_analysis_summary.md        # Rangkuman perbaikan 13 bug & audit keamanan
│   ├── free_hosting_guide.md          # Panduan hosting gratis selamanya (Docker/VPS)
│   ├── huggingface_deployment.md      # Panduan deployment instan ke HF Spaces
│   ├── user_guide.md                  # Panduan lengkap penggunaan 5 fitur utama
│   ├── debian_packaging_technical.md  # Dokumentasi teknis automasi paket .deb
│   └── seo_optimization_report.md     # Panduan SEO untuk peringkat #1 Google
├── omniget_1.0.0_amd64.deb # Paket instalasi Debian amd64 siap pasang
└── SHA256SUMS              # Hash SHA-256 untuk verifikasi berkas
```

---

## 📥 Panduan Instalasi Cepat

### 1. Pasang Dependensi Utama
OmniGet membutuhkan `aria2` dan `ffmpeg` untuk berfungsi di sistem host Linux Anda. Jalankan perintah berikut di terminal:

```bash
sudo apt-get update
sudo apt-get install -y aria2 ffmpeg
```

*(Catatan: Pengguna Ubuntu harap memastikan repositori `universe` aktif dengan menjalankan `sudo add-apt-repository universe` jika paket `aria2` tidak ditemukan).*

### 2. Pasang Paket Debian OmniGet
Pasang paket `.deb` yang ada di repositori ini:

```bash
sudo dpkg -i omniget_1.0.0_amd64.deb
```

Jika terdapat galat mengenai dependensi yang belum terpenuhi, perbaiki dengan perintah:
```bash
sudo apt-get install -f -y
```

---

## 🚀 Cara Menjalankan Aplikasi
* **Mengakses Antarmuka Web**:
  Buka browser Anda dan akses **`http://localhost:5000`** atau ketik perintah di bawah ini di terminal:
  ```bash
  omniget
  ```

* **Mengelola Layanan Latar Belakang (Systemd)**:
  Layanan OmniGet berjalan sebagai service daemon di latar belakang.
  ```bash
  # Periksa status layanan
  sudo systemctl status omniget.service
  
  # Menghentikan/menjalankan kembali layanan
  sudo systemctl stop omniget.service
  sudo systemctl start omniget.service
  ```

---

## 🔒 Verifikasi Keamanan Berkas (SHA-256 Checksum)
Untuk memastikan berkas `.deb` yang Anda unduh identik dan tidak mengalami kerusakan selama transfer, lakukan pencocokan hash SHA-256 berikut:

```bash
sha256sum -c SHA256SUMS
```
Hasil verifikasi yang sukses akan memunculkan pesan: `omniget_1.0.0_amd64.deb: OK`.
