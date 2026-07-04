# Panduan Hosting Gratis Selamanya untuk OmniGet

Karena OmniGet adalah aplikasi pengunduh media yang membutuhkan dependensi sistem tingkat rendah (**FFmpeg** untuk penggabungan video dan **aria2c** untuk torrent), Anda **tidak bisa** menggunakan hosting gratis statis (seperti GitHub Pages, Netlify, atau Vercel). 

Anda memerlukan layanan hosting berbasis **Docker / VPS** gratis. Berikut adalah 3 rekomendasi terbaik beserta cara melakukan deployment secara **gratis selamanya**:

---

## 🌟 Opsi 1: Hugging Face Spaces (Docker Space) — *Rekomendasi Utama (Instan & Mudah)*
Hugging Face menyediakan layanan "Spaces" gratis yang memungkinkan Anda menjalankan container Docker kustom dengan alokasi sumber daya yang sangat besar (gratis selamanya!).

* **Spesifikasi Gratis**: 2 vCPU, 16 GB RAM, Penyimpanan Ephemeral (Sangat besar untuk ukuran hosting gratis).
* **Kelebihan**: RAM besar (16GB) sangat membantu saat memproses penggabungan video resolusi tinggi dengan FFmpeg.
* **Kekurangan**: Server akan masuk ke mode tidur (*sleep*) jika tidak ada pengunjung selama 48 jam (tetapi otomatis aktif kembali secara instan saat diakses).

### Langkah Deployment:
1. Daftar akun gratis di [Hugging Face](https://huggingface.co/).
2. Klik tombol **New Space** di menu profil.
3. Atur konfigurasi Space:
   * **Space Name**: `omniget` (atau bebas).
   * **SDK**: Pilih **Docker**.
   * **Template**: Pilih **Blank** (atau *None*).
   * **Space License**: Apache 2.0 (atau bebas).
   * **Visibility**: **Public** (agar bisa diakses semua orang).
4. Klik **Create Space**.
5. Upload seluruh berkas proyek Anda (termasuk berkas **`Dockerfile`** dan **`requirements.txt`** yang baru saja kami buat) ke tab **Files** di Space Anda, atau push menggunakan Git.
6. Hugging Face akan membangun (*build*) kontainer secara otomatis dan mempublish aplikasi Anda dalam hitungan menit!

> [!NOTE]  
> Hugging Face berjalan pada port `7860`. Kami telah mengonfigurasi Dockerfile agar kompatibel secara otomatis.

---

## 🚀 Opsi 2: Oracle Cloud Always Free Compute (VPS Ubuntu Gratis Selamanya)
Oracle menyediakan 2 VM virtual server berbasis ARM gratis selamanya. Ini adalah VPS mandiri, sehingga Anda memiliki kendali penuh atas sistem operasi.

* **Spesifikasi Gratis**: 4 Ampere A1 Core CPU, 24 GB RAM, 200 GB SSD Storage (Bisa dibagi hingga 2 VM).
* **Kelebihan**: Selalu aktif (*Always-On*, tidak pernah tidur), memiliki IP Publik sendiri, penyimpanan SSD besar, dan performa tinggi.
* **Kekurangan**: Memerlukan pendaftaran dengan verifikasi kartu kredit (hanya untuk validasi identitas, saldo tidak akan dipotong/tagihan Rp 0).

### Langkah Deployment:
1. Daftar di [Oracle Cloud Free Tier](https://www.oracle.com/cloud/free/).
2. Buat instance Compute baru menggunakan **Ubuntu OS** dan **Ampere (ARM) Shape** (Pilih alokasi 2 atau 4 OCPU dan 12 atau 24 GB RAM).
3. Setelah VPS aktif, hubungkan via SSH, lalu install dependensi:
   ```bash
   sudo apt update
   sudo apt install -y python3-pip python3-venv ffmpeg aria2c git
   ```
4. Clone proyek Anda, buat virtual environment, install requirements, dan jalankan server Flask di latar belakang (misalnya menggunakan `nohup` atau `systemd`).

---

## ⚡ Opsi 3: Koyeb (Docker App)
Koyeb adalah alternatif modern seperti Heroku yang mendukung kontainerisasi Docker dengan gratis selamanya.

* **Spesifikasi Gratis**: 1 Service, 512 MB RAM, 0.1 vCPU.
* **Kelebihan**: Antarmuka deployment modern, langsung terhubung dengan GitHub.
* **Kekurangan**: RAM 512 MB cukup kecil untuk pemrosesan FFmpeg skala besar, dan server akan tidur jika tidak ada aktivitas.

### Langkah Deployment:
1. Buat akun di [Koyeb](https://www.koyeb.com/).
2. Hubungkan akun Koyeb Anda dengan repositori GitHub proyek OmniGet.
3. Koyeb akan mendeteksi berkas **`Dockerfile`** secara otomatis.
4. Klik **Deploy** dan Koyeb akan meluncurkan aplikasi Anda ke internet.
