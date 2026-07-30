# Panduan Langkah Demi Langkah Deployment ke Hugging Face Spaces

Hugging Face Spaces (Docker) adalah cara tercepat dan termudah untuk mempublikasikan OmniGet secara gratis selamanya dengan kapasitas server yang besar.

Kami telah menyesuaikan berkas **`Dockerfile`** proyek Anda secara khusus agar kompatibel dengan kebijakan port (`7860`) dan hak akses keamanan pengguna non-root (`UID 1000`) di Hugging Face.

---

## 🚀 Langkah 1: Persiapan Akun & Space Baru
1. Masuk atau daftar akun di [Hugging Face](https://huggingface.co/).
2. Di pojok kanan atas, klik foto profil Anda dan pilih **New Space**.
3. Isi detail pembuatan Space:
   * **Space Name**: `omniget` (atau nama lain yang Anda sukai).
   * **License**: Pilih `apache-2.0` (atau biarkan default).
   * **SDK**: Pilih **Docker** (Wajib).
   * **Docker Template**: Pilih **Blank** / **None** (Wajib).
   * **Space Hardware**: Pilih **Cpu basic • 2 vCPU • 16 GB • Free** (Gratis).
   * **Visibility**: Pilih **Public** agar website Anda bisa diakses oleh publik.
4. Klik tombol **Create Space**.

---

## 📂 Langkah 2: Mengunggah Kode Aplikasi
Hugging Face menggunakan repositori Git untuk mengelola kode. Anda bisa mengunggah berkas kode dengan dua cara:

### Cara A: Unggah Langsung via Browser (Untuk Pemula)
1. Setelah Space dibuat, buka tab **Files and versions** di halaman Space Anda.
2. Klik tombol **Add file** > **Upload files**.
3. Drag & drop seluruh isi folder proyek OmniGet Anda.
   > [!IMPORTANT]  
   > Pastikan berkas **`Dockerfile`**, **`requirements.txt`**, dan berkas utama lainnya terunggah di tingkat root direktori Space Anda.
4. Klik **Commit changes to main** di bagian bawah.

### Cara B: Menggunakan Git CLI (Direkomendasikan)
1. Salin perintah clone dari halaman Space Anda (misalnya):
   ```bash
   git clone https://huggingface.co/spaces/username/omniget
   ```
2. Salin seluruh isi proyek OmniGet ke dalam folder hasil clone tersebut.
3. Commit dan push ke Hugging Face:
   ```bash
   git add .
   git commit -m "Initial commit to Hugging Face"
   git push
   ```

---

## ⚙️ Langkah 3: Menunggu Proses Build & Menjalankan Website
1. Setelah berkas terunggah, Hugging Face secara otomatis mendeteksi **`Dockerfile`** Anda dan memulai proses instalasi OS (termasuk FFmpeg & aria2c) serta paket Python.
2. Anda dapat melihat log proses build secara langsung di tab **App** pada Space Anda.
3. Setelah status berubah menjadi **Running** (berwarna hijau), website OmniGet Anda sudah aktif dan siap digunakan secara publik!
4. Tautan akses website Anda akan berbentuk:
   `https://huggingface.co/spaces/username/omniget` (atau klik tombol **Embed this Space** > **Direct URL** untuk mendapatkan tautan layar penuh).
