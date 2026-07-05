---
title: OmniGet
emoji: ☁️
colorFrom: purple
colorTo: indigo
sdk: docker
app_port: 7860
pinned: false
---

# OmniGet - Universal Media Downloader & P2P Torrent Client

OmniGet adalah aplikasi web pengunduh media multi-fungsi berskala premium berbasis Python (Flask) dan antarmuka web modern (Vanilla HTML/CSS/JS dengan visual Glassmorphism). Aplikasi ini dirancang untuk memberikan pengalaman pengunduhan yang cepat, aman, dan tanpa iklan untuk berbagai jenis konten digital.

---

## 🚀 Fitur Utama

1. **Universal Video & Audio Downloader**:
   * Mengunduh video (MP4) hingga resolusi 1080p dan audio (MP3) dari YouTube, TikTok, dan puluhan platform lainnya menggunakan `yt-dlp`.
   * Integrasi pemotongan waktu (*ffmpeg media trimming*) secara presisi sebelum berkas dikirim ke pengguna.
   * Multi-threaded Segmented Downloader untuk mempercepat pengunduhan berkas langsung.
2. **P2P Torrent Downloader**:
   * Pengunduhan magnet link dan file `.torrent` menggunakan engine backend berkinerja tinggi `aria2c`.
   * Isolasi proses unduhan torrent untuk menjamin keamanan data dan menghindari bentrokan berkas (*race condition*).
3. **Site Media Grabber**:
   * Menjelajahi dan menyaring (*crawling*) seluruh berkas gambar, video, audio, dan dokumen dari halaman website apa saja secara instan.
4. **Keamanan Kelas Industri (Hardened Security)**:
   * Proteksi penuh terhadap celah *Server-Side Request Forgery* (SSRF) dan bypass pengalihan HTTP 302.
   * Perlindungan terhadap *DOM-based Cross-Site Scripting* (XSS) melalui sanitasi keluaran dinamis.
   * Pencegahan eksploitasi *Path Traversal* dan *Argument Injection*.
5. **Manajemen Penyimpanan Otomatis**:
   * Daemon latar belakang pembersih berkas kedaluwarsa secara berkala (menghapus berkas dan folder isolasi berusia > 10 menit untuk mencegah kebocoran *disk space*).

---

## 📁 Struktur Proyek & Indeks Dokumentasi

```text
media_downloader/
├── app.py                     # Entrypoint aplikasi Flask
├── config.py                  # Konfigurasi global & status penyimpanan memori
├── Dockerfile                 # Konfigurasi kontainerisasi Hugging Face Spaces & Docker
├── requirements.txt           # Daftar dependensi Python produksi
├── core/                      # Engine logika utama
│   ├── cleanup.py             # Daemon pembersih berkas sampah & direktori isolasi
│   ├── security.py            # Validasi URL (SSRF) & wrapper HTTP client aman
│   ├── torrent_engine.py      # Integrasi pengunduh P2P aria2c
│   └── ytdlp_engine.py        # Integrasi parser yt-dlp & pemrosesan ffmpeg
├── routes/                    # API Endpoints (Flask Blueprints)
│   ├── download.py            # API Unduhan universal, berkas, & lirik
│   ├── grabber.py             # API crawling media situs web
│   ├── main.py                # Route web statis & status server
│   └── torrent.py             # API unggah & pemrosesan torrent
├── static/                    # Aset statis (CSS, JS, robots.txt, sitemap.xml)
├── templates/
│   └── index.html             # Antarmuka Glassmorphism Premium
└── docs/                      # Pusat Dokumentasi Lengkap
    ├── bug_analysis_summary.md # Laporan detail 12 bug & perbaikan keamanan
    ├── huggingface_deployment.md # Panduan langkah demi langkah rilis ke Hugging Face
```

Silakan tinjau folder **[docs/](file:///home/andi-liani/code/media_downloader/docs/)** untuk mempelajari arsitektur teknis lebih mendalam.

---

## 🛠️ Persyaratan Sistem Lokal

* **Sistem Operasi**: Linux / macOS / Windows
* **Python**: Versi 3.12+ (Virtual environment dikonfigurasi pada `/home/andi-liani/virtual/venv`)
* **Dependensi Sistem**:
  * `ffmpeg` (Untuk konversi audio dan penggabungan video)
  * `aria2c` (Untuk mengunduh file P2P Torrent)

---

## 💻 Cara Menjalankan Secara Lokal

1. Pastikan dependensi sistem (`ffmpeg` dan `aria2c`) sudah terpasang dan dapat diakses di PATH.
2. Aktifkan virtual environment Anda dan install dependensi:
   ```bash
   source /home/andi-liani/virtual/venv/bin/activate
   pip install -r requirements.txt
   ```
3. Jalankan aplikasi Flask:
   ```bash
   python app.py
   ```
4. Buka browser Anda dan akses: **[http://localhost:5000](http://localhost:5000)**
