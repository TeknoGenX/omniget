# Rekapitulasi Perbaikan Seluruh Bug & Keamanan OmniGet

Kami telah melakukan audit mendalam terhadap seluruh struktur kode OmniGet dan berhasil mengidentifikasi serta memperbaiki total **12 bug dan kerentanan keamanan** secara otomatis.

Aplikasi Anda kini sudah berada dalam kondisi yang sangat aman, stabil, dan siap digunakan.

---

## 🛡️ Rangkuman Perbaikan Keamanan (Security Fixes)

### 1. Celah *Path Traversal* pada Unduhan Lirik (Tingkat: Kritis)
* **Status**: ✅ **Selesai Diperbaiki**
* **Temuan**: Penggunaan parameter format (`fmt`) tanpa sanitasi memungkinkan pembacaan berkas sensitif dari sistem operasi (seperti `/etc/passwd`).
* **Perbaikan**: Nilai `fmt` kini dibatasi secara ketat hanya untuk ekstensi `.txt` dan `.lrc`.

### 2. Celah *Arbitrary File Upload* pada Unggahan Torrent (Tingkat: Kritis - Risiko RCE)
* **Status**: ✅ **Selesai Diperbaiki**
* **Temuan**: Nama berkas torrent yang diunggah (`file.filename`) digunakan secara langsung tanpa sanitasi, memungkinkan penimpaan berkas kode program server.
* **Perbaikan**: Mengintegrasikan `secure_filename` untuk membersihkan nama berkas sebelum disimpan.

### 3. Kerentanan *Server-Side Request Forgery* (SSRF) (Tingkat: Tinggi)
* **Status**: ✅ **Selesai Diperbaiki**
* **Temuan**: Aplikasi menerima dan memproses URL dari pengguna secara mentah, berpotensi memindai atau mengeksploitasi jaringan privat server.
* **Perbaikan**: Memasang fungsi resolusi DNS di `core/security.py` untuk memblokir rentang IP lokal, privat, loopback, dan multicast.

### 4. Bypass SSRF Melalui Pengalihan HTTP (Redirect-based SSRF) (Tingkat: Tinggi)
* **Status**: ✅ **Selesai Diperbaiki**
* **Temuan**: Penyerang menggunakan URL publik yang dialihkan (302 redirect) ke IP privat internal untuk mengelabui validasi IP awal.
* **Perbaikan**: Membuat wrapper `safe_requests_get` and `safe_requests_head` dengan mematikan pengalihan otomatis dan memvalidasi setiap URL pengalihan secara manual.

### 5. Celah *Argument Injection* pada aria2c (Tingkat: Sedang)
* **Status**: ✅ **Selesai Diperbaiki**
* **Temuan**: Input URL torrent yang diawali dengan tanda hubung (`-`) dapat dievaluasi sebagai opsi parameter tambahan pada perintah eksekusi CLI `aria2c`.
* **Perbaikan**: Menambahkan penanda batas opsi `--` sebelum menyisipkan variabel URL di perintah aria2c.

### 6. Kerentanan DOM-based Cross-Site Scripting (XSS) (Tingkat: Tinggi)
* **Status**: ✅ **Selesai Diperbaiki**
* **Temuan**: Data input luar seperti judul video, nama berkas yang di-grab, dan riwayat diinterpolasikan mentah-mentah ke DOM menggunakan `.innerHTML`, membuka celah eksekusi JavaScript jahat.
* **Perbaikan**: Membuat fungsi pembantu `escapeHtml(text)` di frontend JavaScript dan menyaring seluruh data dinamis sebelum dirender.

---

## ⚙️ Rangkuman Perbaikan Stabilitas & Logika (Stability & Logic Fixes)

### 7. *RuntimeError* Modifikasi Kamus Konkuren pada Pembersih Tugas
* **Status**: ✅ **Selesai Diperbaiki**
* **Temuan**: Modifikasi konkuren dari thread Flask memicu kegagalan iterasi di thread latar belakang pembersihan.
* **Perbaikan**: Menggunakan salinan daftar kunci `list(download_tasks.keys())` untuk melintasi tugas.

### 8. *RuntimeError* Modifikasi Kamus Konkuren pada API Status Server
* **Status**: ✅ **Selesai Diperbaiki**
* **Temuan**: Masalah yang sama dengan daemon pembersih, terjadi saat rute `/api/server/status` diakses bersamaan dengan pembuatan tugas baru.
* **Perbaikan**: Menerapkan metode penghitungan tugas aktif secara thread-safe menggunakan salinan kunci.

### 9. *Race Condition* Penamaan Berkas pada Unduhan Torrent Simultan
* **Status**: ✅ **Selesai Diperbaiki**
* **Temuan**: Penggunaan `mtime` global untuk menemukan hasil unduhan torrent dapat menyebabkan file pengguna tertukar jika diunduh bersamaan.
* **Perbaikan**: Mengisolasi proses unduhan setiap tugas ke folder khusus `downloads/<task_id>/` sebelum dipindahkan ke folder utama.

### 10. Validasi Format Waktu untuk Pemotongan Media (*Trim*)
* **Status**: ✅ **Selesai Diperbaiki**
* **Temuan**: Parameter waktu potong video dimasukkan langsung ke argumen `ffmpeg` tanpa pengecekan format.
* **Perbaikan**: Memasang ekspresi reguler (Regex) untuk memvalidasi parameter `start_time` dan `end_time` agar sesuai dengan format waktu sebelum dieksekusi.

### 11. Gagal Deteksi Ekstensi Torrent karena secure_filename Kosong
* **Status**: ✅ **Selesai Diperbaiki**
* **Temuan**: Nama file torrent berisi karakter tidak aman sepenuhnya mengembalikan string kosong `""` setelah dibersihkan, merusak format file eksekusi aria2c.
* **Perbaikan**: Memberikan nilai fallback `'download.torrent'` jika hasil sanitasi bernilai kosong.

### 12. Kebocoran Direktori Sementara (Directory & Disk Space Leak) pada Cleanup Daemon
* **Status**: ✅ **Selesai Diperbaiki**
* **Temuan**: Folder isolasi torrent `downloads/<task_id>/` yang gagal/batal diunduh tidak terdeteksi oleh pembersih berkas lama karena berupa direktori, menyisakan berkas sampah.
* **Perbaikan**: Memperluas cakupan pembersihan agar dapat menghapus direktori secara rekursif (`shutil.rmtree`) jika umurnya telah melebihi 10 menit.
