# Movie Genre Prediction - End-to-End ML Production

Proyek ini adalah implementasi sistem AI *End-to-End* untuk memprediksi genre film berdasarkan teks sinopsis (overview). Proyek ini dibangun untuk memenuhi persyaratan tugas akhir bootcamp **AI System Project (End-to-End ML Production)**.

## Fitur & Komponen Project (Sesuai Rubrik)

1. **Data Versioning**: Pengelolaan dataset menggunakan `DVC` (Data Version Control). Data disimpan di folder `data/` (diabaikan oleh Git, dikelola oleh DVC).
2. **Model Versioning**: Pelacakan eksperimen dan model menggunakan `MLflow`. Semua hiperparameter, metrik, dan artifak model tersimpan dengan rapi.
3. **Code Versioning**: Version control kode base menggunakan `Git` dan `GitHub`.
4. **Image Versioning**: Kontainerisasi aplikasi menggunakan `Docker`. Image dapat didorong (push) ke Docker Hub.
5. **Model Serving & Deployment**: Penyajian model (serving) melalui REST API menggunakan `FastAPI`. Siap di-deploy ke Cloud (Render/Railway/AWS).

---

## Persiapan Lingkungan (Setup Lingkungan Lokal)

Pastikan Anda sudah menginstal Python (disarankan 3.10+), Git, dan Docker di komputer Anda.

### 1. Clone Repository
```bash
git clone https://github.com/mtijan/Movie_genre_prediction.git
cd Movie_genre_prediction
```

### 2. Buat Virtual Environment
Dianjurkan menggunakan virtual environment agar *dependencies* tidak bentrok.
```bash
# Membuat virtual environment bernama 'venv'
python -m venv venv

# Mengaktifkan venv (Windows)
.\venv\Scripts\activate

# Mengaktifkan venv (Mac/Linux)
source venv/bin/activate
```

### 3. Instal Kebutuhan Library (Dependencies)
```bash
pip install -r requirements.txt
```

---

## Cara Menjalankan AI System

### Langkah 1: Pelatihan & Rekam Model (MLflow)
Langkah pertama adalah melatih model. Model yang digunakan adalah `LinearSVC` dipadu dengan `TF-IDF Vectorizer`. Proses ini akan otomatis terekam oleh MLflow.

Pastikan file dataset berada di `data/movies.csv`.

Jalankan perintah berikut untuk melatih model:
```bash
python src/train.py
```
**Apa yang terjadi?**
- Model akan membaca data dari `data/movies.csv`.
- Memisahkan kumpulan data (Train/Test).
- Melakukan pelatihan (Training).
- Menyimpan parameter, metrik (akurasi), dan model ke dalam folder `mlruns/` (MLflow).
- Menyimpan salinan model ke folder `models/` (untuk digunakan oleh API).

Untuk melihat dasbor rekaman eksperimen MLflow, jalankan:
```bash
mlflow ui
```
Lalu buka `http://localhost:5000` di peramban (browser) Anda.

### Langkah 2: Menjalankan Model API (FastAPI) Lokal
Setelah model terlatih dan tersimpan di folder `models/`, kini Anda siap menghidupkan server API lokal.

Jalankan server menggunakan uvicorn:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
API sekarang aktif. Anda bisa mencobanya dengan beberapa cara:
1. **Buka Swagger UI (Antarmuka Web API Interaktif)**: Kunjungi http://localhost:8000/docs
2. **Endpoint Prediksi (`/predict`)**: Cobalah mengirimkan permintaan POST (via Swagger UI atau alat `curl` di terminal):
```bash
curl -X 'POST' \
  'http://localhost:8000/predict' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "overview": "A group of elite soldiers must fight through enemy territory on a dangerous military mission to rescue hostages."
}'
```

### Langkah 3: Menjalankan Menggunakan Docker (Kontainerisasi)
Untuk membuktikan bahwa sistem ini portabel dan siap dideploy, Anda bisa membungkusnya dalam satu kontainer Docker.

**1. Membangun (Build) Docker Image:**
```bash
docker build -t movie-genre-api:v1.0 .
```

**2. Menjalankan Docker Container:**
```bash
docker run -d -p 8000:8000 --name movie_api movie-genre-api:v1.0
```
Sekarang coba buka lagi http://localhost:8000/docs. API Anda sekarang hidup melayani prediksi dari dalam Docker!

**3. Mendorong (Push) Image ke Docker Hub:**
Ubah `username_anda` dengan username Docker Hub Anda.
```bash
docker tag movie-genre-api:v1.0 username_anda/movie-genre-api:v1.0
docker push username_anda/movie-genre-api:v1.0
```

---

## Checklist Implementasi Tugas

- [x] **Data Versioning:** Folder data sudah diabaikan di `.gitignore`. Disarankan untuk menginstal DVC (`pip install dvc dvc-s3/dvc-gdrive`) dan menjalankan: `dvc init`, `dvc add data/movies.csv`, lalu `git add data/movies.csv.dvc`.
- [x] **Model Versioning:** Sudah menggunakan MLflow (lihat skrip `src/train.py`).
- [x] **Code Versioning:** Repo GitHub (`main` branch) berisi struktur kode lengkap.
- [x] **Image Versioning:** File `Dockerfile` tersedia dengan instalasi yang bersih.
- [x] **Model Serving:** Menggunakan FastAPI (`app/main.py`), siap di-deploy ke Cloud (Render/Railway).

---

## Struktur Folder
```text
Movie_genre_prediction/
├── app/
│   ├── __init__.py
│   ├── main.py          # FastAPI application
│   └── schemas.py       # Pydantic validation models
├── data/
│   └── movies.csv       # Dataset (Not tracked by git, use DVC)
├── models/
│   ├── model.pkl        # Compressed Model
│   └── vectorizer.pkl   # TF-IDF Features
├── notebooks/           # Jupyter notebooks for EDA & data preparation
├── src/
│   ├── predict.py       # Code loaded by API to trigger predictions
│   └── train.py         # Code to train model & log via MLflow
├── Dockerfile           # Blueprint of Docker image
├── .dockerignore        # Unnecessary files in Docker image
├── requirements.txt     # Python Library lists
└── README.md            # You are reading this
```
