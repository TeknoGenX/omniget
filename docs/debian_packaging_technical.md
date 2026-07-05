# Dokumentasi Teknis Pembuatan Paket Debian (.deb)

Berkas ini mendokumentasikan spesifikasi, struktur, dan proses otomatisasi pembangunan paket Debian (`.deb`) untuk **OmniGet**.

---

## 🛠️ Alat Pembangun (Build Automator)

Pembangunan paket dikelola oleh skrip bash:
👉 **[build_deb.sh](file:///home/andi-liani/code/media_downloader/build_deb.sh)**

Skrip ini secara otomatis membuat struktur direktori Debian standar, menulis berkas kontrol, post/pre scripts, menyalin source code program, mengatur izin berkas (*permissions*), dan memicu perintah `dpkg-deb --build` untuk menghasilkan berkas `.deb` siap pasang.

---

## 📂 Struktur Paket yang Dihasilkan

Setelah diekstraksi, paket Debian memetakan berkas ke lokasi sistem sebagai berikut:

```text
/
├── usr/
│   ├── bin/
│   │   └── omniget                   # CLI launcher (membuka browser ke http://localhost:5000)
│   └── share/
│       └── omniget/                  # Direktori utama kode sumber aplikasi
│           ├── app.py
│           ├── config.py
│           ├── requirements.txt
│           ├── core/
│           ├── routes/
│           ├── static/
│           └── templates/
├── lib/
│   └── systemd/
│       └── system/
│           └── omniget.service       # Service systemd untuk daemon background
└── DEBIAN/
    ├── control                       # Metadata paket & daftar dependensi APT
    ├── postinst                      # Skrip pasca-instalasi (konfigurasi venv & systemd)
    ├── prerm                         # Skrip pra-penghapusan (menghentikan service)
    └── postrm                        # Skrip pasca-penghapusan (pembersihan user & data)
```

---

## ⚙️ Skrip Kontrol Debian (Maintainer Scripts)

### 1. `control` (Metadata & Dependensi)
Mendeklarasikan metadata paket. Dependensi yang ditentukan adalah:
* **`python3`**, **`python3-venv`**, **`python3-pip`** (kebutuhan runtime Python).
* **`ffmpeg`** (pemrosesan format video/audio).
* **`aria2`** (backend pengunduhan P2P torrent).

### 2. `postinst` (Post-Installation)
Menangani setup lingkungan setelah berkas disalin ke sistem:
1. Membuat user system bernama `omniget` (tanpa home direktori & shell login) untuk menjalankan aplikasi secara terisolasi demi keamanan sandboxing.
2. Membuat Python Virtual Environment (venv) di `/usr/share/omniget/venv`.
3. Menginstal seluruh dependensi Python yang tercantum di `requirements.txt` ke dalam venv secara otomatis.
4. Membuat direktori penyimpanan unduhan di `/var/lib/omniget/downloads` dan mengatur kepemilikan (`chown`) ke user `omniget`.
5. Membuat symlink dari `/usr/share/omniget/downloads` ke `/var/lib/omniget/downloads`.
6. Mendaftarkan, mengaktifkan (*enable*), dan menjalankan (*start*) unit layanan systemd `omniget.service`.

### 3. `prerm` (Pre-Removal)
Dijalankan sebelum paket dihapus:
1. Menghentikan (*stop*) unit layanan systemd `omniget.service`.
2. Menonaktifkan (*disable*) unit layanan systemd agar tidak dijalankan saat startup.

### 4. `postrm` (Post-Removal)
Dijalankan setelah paket dihapus:
1. Menghapus daemon unit systemd dari sistem.
2. Menghapus user system `omniget`.
3. Menghapus direktori `/usr/share/omniget` (source code & venv).
4. **Opsional (Purge)**: Jika pengguna menjalankan `apt purge`, skrip akan menghapus seluruh sisa data unduhan di `/var/lib/omniget`.
