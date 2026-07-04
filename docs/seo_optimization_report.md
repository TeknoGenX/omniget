# Panduan Optimalisasi SEO OmniGet (Menuju Peringkat #1 Google)

Kami telah menerapkan standar optimalisasi SEO (Search Engine Optimization) terbaik pada berkas kode aplikasi OmniGet untuk memastikan website Anda diindeks secara sempurna oleh mesin pencari (terutama Google) saat di-publish di internet.

---

## 🛠️ Langkah Optimalisasi yang Telah Diterapkan

### 1. Meta Tags & Header SEO Komplit
Kami memperbarui bagian `<head>` pada berkas `templates/index.html` dengan:
* **Title Tag Tertarget**: Mengubah title menjadi `"OmniGet - Download Video YouTube & Media Downloader Gratis"` untuk mencocokkan kata kunci pencarian volume tinggi.
* **Meta Description**: Deskripsi web yang komprehensif dan menarik perhatian CTR (*Click-Through Rate*) user.
* **Meta Keywords & Robots**: Penambahan meta kata kunci relevan dan instruksi eksplisit `"index, follow"` untuk robot crawler Google.
* **Canonical URL**: Ditambahkan tag canonical untuk mencegah isu konten duplikat (*duplicate content penalty*).

### 2. Open Graph & Twitter Cards
Menambahkan metadata Open Graph (OG) dan Twitter Cards agar tampilan website terlihat profesional dan memiliki thumbnail menarik saat dibagikan ke platform media sosial (Facebook, WhatsApp, LinkedIn, Twitter/X).

### 3. Google JSON-LD Structured Data
Menambahkan metadata terstruktur standar Schema.org tipe `WebApplication`. Ini membantu Google menampilkan website Anda sebagai "Rich Snippet" di halaman hasil pencarian (menampilkan deskripsi aplikasi, rating, sistem operasi, serta harga gratis `0.00 USD`).

### 4. Crawler indexing (robots.txt & sitemap.xml)
* Membuat berkas `static/robots.txt` untuk mengizinkan bot merayapi seluruh halaman.
* Membuat berkas sitemap dinamis `static/sitemap.xml` yang mendaftarkan URL berprioritas `1.0`.
* Menambahkan rute Flask pada `routes/main.py` agar berkas robots.txt dan sitemap.xml dapat diakses langsung oleh Google Bot di root domain (`/robots.txt` & `/sitemap.xml`).

---

## 🚀 Langkah Wajib Saat Publish di Internet agar Masuk Peringkat #1

Agar website Anda bisa tampil di urutan teratas, Anda wajib melakukan 5 langkah eksternal berikut setelah domain Anda aktif:

### 1. Daftarkan Domain ke Google Search Console (GSC)
1. Buka [Google Search Console](https://search.google.com/search-console).
2. Tambahkan properti baru menggunakan alamat domain Anda (misal: `https://omniget-downloader.com`).
3. Lakukan verifikasi kepemilikan domain (menggunakan DNS TXT Record).
4. Masuk ke menu **Sitemaps**, lalu daftarkan URL sitemap Anda: `https://omniget-downloader.com/sitemap.xml`.

### 2. Gunakan SSL / HTTPS (Sangat Penting)
Google secara resmi memprioritaskan website yang menggunakan HTTPS dan memberikan penalti (peringkat diturunkan) bagi website HTTP biasa. Gunakan SSL gratis dari **Let's Encrypt** (atau Cloudflare SSL) saat melakukan deployment.

### 3. Pasang Cloudflare untuk Kecepatan & Keamanan
1. Kecepatan loading halaman (*Page Speed*) adalah metrik utama Google Core Web Vitals.
2. Salurkan trafik domain Anda melalui Cloudflare CDN untuk melakukan caching statis aset dan mempercepat loading web hingga di bawah 1 detik secara global.

### 4. Bangun Backlink Berkualitas (Link Building)
Google menilai otoritas website berdasarkan seberapa banyak website terpercaya lain yang merujuk/menautkan link ke website Anda.
* Bagikan OmniGet di forum-forum pengembang (Reddit r/selfhosted, ProductHunt, GitHub).
* Tulis artikel ulasan atau bagikan di media sosial untuk memicu backlinks alami.

### 5. Sesuaikan URL Canonical di Templates
Sebelum melakukan deployment produksi, pastikan Anda mengganti kata kunci `http://localhost:5000/` pada tag canonical, OG tags, dan JSON-LD di berkas `templates/index.html` dengan domain produksi asli Anda (contoh: `https://omniget-downloader.com/`).
