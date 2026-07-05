# Panduan Instalasi OmniGet (.deb)

Berkas ini memuat instruksi lengkap untuk memasang dan menjalankan **OmniGet** menggunakan paket Debian `.deb` di sistem operasi berbasis Linux (Ubuntu, Debian, Mint, dll.).

---

## 🛠️ Prasyarat Sistem

Sebelum memulai pemasangan, pastikan sistem Anda memenuhi prasyarat berikut:
* **Sistem Operasi**: Ubuntu 20.04+, Debian 11+, atau distribusi turunannya.
* **Python**: Versi 3.10 ke atas (akan otomatis dikonfigurasi menggunakan venv).
* **Layanan Systemd**: Diperlukan untuk menjalankan OmniGet daemon secara otomatis di latar belakang.

---

## 📥 Langkah-Langkah Pemasangan

### 1. Memasang Dependensi Pendukung secara Manual
OmniGet membutuhkan pengunduh BitTorrent `aria2` dan pemroses media `ffmpeg`. Jalankan perintah berikut untuk memasangnya:

```bash
# Perbarui daftar paket Anda
sudo apt-get update

# Pasang dependensi utama
sudo apt-get install -y aria2 ffmpeg
```

*(Catatan: Pengguna Ubuntu perlu memastikan repositori `universe` telah aktif dengan menjalankan `sudo add-apt-repository universe` jika paket `aria2` tidak ditemukan).*

### 2. Memasang Paket `.deb` OmniGet
Gunakan `dpkg` untuk memasang berkas paket Debian OmniGet:

```bash
sudo dpkg -i omniget_1.0.0_amd64.deb
```

Jika terdapat galat mengenai dependensi yang belum terpenuhi saat pemasangan, perbaiki dengan perintah:
```bash
sudo apt-get install -f -y
```

---

## 🚀 Cara Menjalankan & Mengelola Layanan

Setelah instalasi selesai, OmniGet akan otomatis berjalan di latar belakang sebagai service Systemd.

* **Akses Antarmuka Web**:
  Buka browser Anda dan akses **`http://localhost:5000`** atau ketik perintah di bawah ini di terminal Anda:
  ```bash
  omniget
  ```

* **Memeriksa Status Layanan**:
  ```bash
  sudo systemctl status omniget.service
  ```

* **Menghentikan Layanan**:
  ```bash
  sudo systemctl stop omniget.service
  ```

* **Menjalankan Kembali Layanan**:
  ```bash
  sudo systemctl start omniget.service
  ```

---

## 🗑️ Cara Menghapus Aplikasi

Jika Anda ingin menghapus aplikasi OmniGet secara permanen beserta seluruh datanya dari sistem:

```bash
sudo apt-get purge omniget
```
Perintah `purge` akan menghapus seluruh source code, service systemd, user `omniget`, serta seluruh riwayat dan berkas unduhan di direktori `/var/lib/omniget`.
