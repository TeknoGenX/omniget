# Changelog - OmniGet

Semua perubahan penting pada proyek **OmniGet** akan didokumentasikan di berkas ini.

## [1.0.0] - 2026-07-05

### Added
- Integrasi P2P Torrent web downloader berbasis backend engine `aria2c`.
- Multi-threaded segmented downloader untuk meningkatkan kecepatan unduhan berkas langsung hingga 4x lipat.
- Site Media Grabber (crawling) untuk mengekstrak dan mengunduh berkas gambar, video, audio, dan dokumen dari situs web mana saja secara massal.
- Skrip otomatisasi pembuatan paket instalasi Debian (`build_deb.sh`).
- Integrasi Bookmarklet pintar untuk menganalisis tautan YouTube/TikTok secara instan hanya dengan sekali klik dari bilah bookmark browser.
- Opsi pembatasan kecepatan (speed limiter) dinamis saat pengunduhan di server maupun pengunduhan lokal ke PC klien.
- Dukungan penjadwalan unduhan di latar belakang berdasarkan input tanggal dan waktu.

### Fixed
- **Keamanan (SSRF)**: Menambahkan modul perlindungan SSRF yang memblokir rentang IP loopback, lokal, privat, dan multicast, serta pencegahan SSRF bypass melalui status redirect 302.
- **Keamanan (Path Traversal)**: Membatasi parameter format subtitel (`fmt`) hanya untuk ekstensi `.txt` dan `.lrc` yang aman untuk mencegah eksploitasi pembacaan berkas sistem host.
- **Keamanan (Argument Injection)**: Menambahkan batas opsi `--` pada perintah aria2c untuk menghindari eksploitasi parameter CLI.
- **Keamanan (XSS)**: Mengintegrasikan fungsi penyaring HTML (`escapeHtml`) di frontend JavaScript untuk menghindari eksploitasi DOM-based Cross-Site Scripting.
- **Fungsi Daemon Pembersih**: Memperluas pembersihan agar mengabaikan direktori/berkas yang terkait dengan tugas unduhan aktif agar tidak terhapus di tengah jalan pada unduhan > 10 menit.
- **Keamanan Unggah Torrent**: Menyaring nama berkas menggunakan `secure_filename` dengan nilai fallback aman untuk mencegah penimpaan file program (Arbitrary File Upload).
- **Concurrency/Thread Safety**: Memperbaiki `RuntimeError: dictionary changed size during iteration` di thread pemantau progress unduhan segmen paralel.
- **File Penamaan**: Menambahkan nilai fallback aman ketika pembersihan judul menghasilkan string kosong (menghindari dotfiles tersembunyi seperti `".mp4"`).
