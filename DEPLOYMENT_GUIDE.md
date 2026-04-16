# MLOps Deployment Guide: End-to-End API Deployment on VPS

Dokumen ini menjelaskan prosedur teknis secara rinci mengenai cara melakukan deployment aplikasi FastAPI (Machine Learning Module) ke Virtual Private Server (VPS) Ubuntu, mulai dari proses kontainerisasi menggunakan Docker hingga konfigurasi Reverse Proxy dan SSL/TLS menggunakan Nginx dan Certbot.

## 1. Arsitektur Deployment

Aplikasi ini menggunakan arsitektur berikut pada lingkungan production:
- **FastAPI (Uvicorn):** Berjalan di dalam Docker container dan melayani request di port 8000.
- **Docker:** Digunakan untuk isolasi application environment, memastikan kode berjalan konsisten di semua sistem operasi.
- **Nginx:** Bertindak sebagai Reverse Proxy di port 80 dan 443. Nginx menerima permintaan dari publik (internet) dan meneruskannya ke port 8000 di daemon Docker lokal.
- **Let's Encrypt (Certbot):** Menyediakan sertifikat keamanan SSL/TLS otomatis untuk mengaktifkan protokol HTTPS.

## 2. Persiapan Repositori dan Docker (Tahap Lokal)

Sebelum mesin cloud dikonfigurasi, aplikasi harus dibungkus dalam Docker image. Konfigurasi ini diatur melalui file `Dockerfile`.

1. Pastikan file `Dockerfile` sudah mendefinisikan port expose dan perintah uvicorn yang mengarah ke `0.0.0.0`, contohnya:
   ```dockerfile
   FROM python:3.10-slim
   WORKDIR /app
   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt
   COPY . .
   EXPOSE 8000
   CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
   ```

2. Lakukan push perubahan kode base ini ke repositori jarak jauh (misal: GitHub) agar mudah ditarik dari dalam VPS.

## 3. Konfigurasi Server VPS (Ubuntu)

Setelah terkoneksi ke VPS melalui protokol SSH (`ssh username@ip_address`), tahapan awal adalah menyiapkan alat-alat fundamental.

Gunakan otorisasi rute `sudo` jika anda tidak menggunakan akun root.
Jalankan pembaruan sistem dan pemasangan paket yang dibutuhkan:

```bash
sudo apt update
sudo apt install docker.io git nginx certbot python3-certbot-nginx -y
```

Tambahkan grup pengguna saat ini (ubuntu) ke dalam group docker agar perintah docker dapat dieksekusi tanpa awalan sudo secara iteratif (opsional namun direkomendasikan):

```bash
sudo usermod -aG docker ubuntu
```

## 4. Proses Cloning dan Peluncuran Container Docker

1. Lakukan duplikasi repositori anda menggunakan git clone:
   ```bash
   git clone https://github.com/mtijan/Movie_genre_prediction.git
   cd Movie_genre_prediction
   ```

2. Mulai proses *build* Docker image. Eksekusi ini akan memparsing skema `Dockerfile` dan menginstall seluruh package Python yang diinstruksi:
   ```bash
   sudo docker build -t movie-genre-api .
   ```

3. Jalankan Docker container di mode latar belakang (detached daemon). Penggunaan flag `--restart unless-stopped` ditujukan untuk memantik auto-start seandainya sistem perating server mengalami reboot.
   ```bash
   sudo docker run -d -p 8000:8000 --name api-mesin-ai --restart unless-stopped movie-genre-api
   ```

Pada titik ini, aplikasi sebenarnya telah berjalan di `http://ip_vps_anda:8000`, namun belum layak dan tidak aman untuk dipaparkan secara langsung ke internet.

## 5. Konfigurasi Reverse Proxy (Nginx)

Langkah krusial berikutnya adalah merutekan traffic publik agar menggunakan domain standar, dengan Nginx yang beroperasi memblokir pemaparan port internal API.

Diasumsikan domain yang Anda miliki adalah `rubybootcamp.my.id`, dan `A Record` di DNS Management Anda sudah diarahkan ke IP Publik VPS Anda.

1. Buat file konfigurasi spesifik untuk Nginx:
   ```bash
   sudo nano /etc/nginx/sites-available/rubybootcamp
   ```

2. Tempel konfigurasi reverse proxy standar berikut ke dalam file tersebut:
   ```nginx
   server {
       listen 80;
       server_name rubybootcamp.my.id;

       location / {
           proxy_pass http://127.0.0.1:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
       }
   }
   ```

3. Simpan file tersebut, lalu buat symbolic link (symlink) untuk mengaktifkannya di Nginx:
   ```bash
   sudo ln -s /etc/nginx/sites-available/rubybootcamp /etc/nginx/sites-enabled/
   ```

4. Lakukan verifikasi sintaks dan mulai ulang layanan Nginx agar konfigurasi berlaku efektif:
   ```bash
   sudo nginx -t
   sudo systemctl restart nginx
   ```

Sekarang traffic di `http://rubybootcamp.my.id` sudah diteruskan ke port 8000.

## 6. Instalasi Sertifikat SSL/TLS Tertandatangani (HTTPS)

Protokol HTTP memancarkan data secara tertekstual-murni. Menerapkan Enkripsi data adalah prasyarat ML production. Kita akan mengotomasi proses ini dengan bantuan Certbot dari Let's Encrypt.

Jalankan perintah ini:

```bash
sudo certbot --nginx -d rubybootcamp.my.id
```

Interaksi Certbot:
- Masukan alamat email sistem administrator.
- Setujui Terms of Service (`A`).
- Otorisasi pengiriman surel bisa diabaikan dengan (`N`).

Sistem Certbot akan melakukan validasi token DNS eksternal, membuat direktori modifikasi otomatis di berkas Nginx kita, dan meregistrasikan kunci enkripsi publik/provat (`fullchain.pem` dan `privkey.pem`). 

Apabila konsol memberikan balasan `Congratulations! You have successfully enabled HTTPS`, maka arsitektur pipeline Deployment AI End-to-End secara formal telah berhasil dilaksanakan. API Anda siap diuji melalui koneksi terenkripsi.
