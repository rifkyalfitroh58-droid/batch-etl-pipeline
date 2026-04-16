# 🔄 Batch ETL Pipeline — Portofolio Data Engineering

> End-to-end batch ETL pipeline dengan **file ingestion**, validasi data otomatis, transformasi berlapis, dan upsert ke PostgreSQL — dibangun dengan prinsip **modular code** dan **clean code**.

---

## 📌 Deskripsi Project

Pipeline ini memproses file transaksi (CSV/JSON) yang masuk ke folder `input/` secara batch. Setiap file melewati tahap **validasi schema**, **transformasi data**, dan **upsert ke PostgreSQL** — dengan file yang gagal validasi otomatis dipindahkan ke folder `quarantine/` dan file yang berhasil diarsipkan ke `archive/`. Seluruh proses dicatat oleh logger otomatis.

---

## 🏗️ Arsitektur Pipeline

```
input/
  └── transactions.csv
         │
         ▼
    FileWatcher          ← Deteksi file baru di folder input
         │
         ▼
    FileValidator        ← Validasi schema, tipe data, nilai null, status
         │
    ┌────┴────┐
  valid    invalid
    │          │
    ▼          ▼
Transformer  Quarantine  ← File invalid dipindahkan ke quarantine/
    │
    ▼
  Loader                 ← Upsert ke PostgreSQL (insert or update)
    │
    ▼
PostgreSQL               ← Tabel transactions tersimpan
    │
    ▼
Archive                  ← File berhasil dipindahkan ke archive/
```

---

## 🛠️ Tech Stack

| Tools | Kegunaan |
|---|---|
| **Python 3.11** | Bahasa utama pipeline |
| **PostgreSQL** | Database penyimpanan hasil ETL |
| **SQLAlchemy** | Koneksi Python ke PostgreSQL |
| **Pandas** | Membaca, validasi, dan transformasi data |
| **python-dotenv** | Manajemen environment variable |
| **pytest** | Unit testing setiap komponen pipeline |

---

## 📂 Struktur Project

```
batch-etl-pipeline/
│
├── input/                        # Taruh file CSV/JSON di sini
│   └── .gitkeep
│
├── archive/                      # File yang berhasil diproses
│   └── .gitkeep
│
├── quarantine/                   # File yang gagal validasi
│   └── .gitkeep
│
├── logs/                         # Log otomatis tersimpan di sini
│   └── .gitkeep
│
├── pipeline/                     # Core pipeline (modular)
│   ├── __init__.py
│   ├── config.py                 # Konfigurasi DB & path folder
│   ├── watcher.py                # Deteksi file baru
│   ├── validator.py              # Validasi schema & kualitas data
│   ├── transformer.py            # Cleaning & normalisasi
│   ├── loader.py                 # Upsert ke PostgreSQL
│   └── orchestrator.py          # Orkestrasi seluruh pipeline
│
├── tests/                        # Unit tests
│   ├── conftest.py
│   ├── test_validator.py
│   └── test_transformer.py
│
├── .env.example                  # Template environment variable
├── .gitignore
├── conftest.py
├── pyproject.toml
├── requirements.txt
└── README.md
```

---

## ⚙️ Setup & Cara Menjalankan

### 1. Clone Repository

```bash
git clone https://github.com/username/batch-etl-pipeline.git
cd batch-etl-pipeline
```

### 2. Buat Conda Environment

```bash
conda create -n batch-etl python=3.11 -y
conda activate batch-etl
pip install -r requirements.txt
pip install -e .
```

### 3. Setup PostgreSQL

```sql
CREATE DATABASE batch_etl_db;
```

### 4. Konfigurasi Environment Variable

```bash
cp .env.example .env
# Buka .env dan isi password PostgreSQL kamu
```

Isi file `.env`:
```
DB_HOST=localhost
DB_PORT=5432
DB_NAME=batch_etl_db
DB_USER=postgres
DB_PASSWORD=password_kamu
```

### 5. Siapkan File Input

Taruh file CSV atau JSON di folder `input/` dengan format berikut:

```csv
transaction_id,customer_id,amount,transaction_date,status
T001,C001,150000.00,2024-01-10,completed
T002,C002,75000.50,2024-01-11,pending
```

### 6. Jalankan Pipeline

```bash
cd pipeline
python orchestrator.py
```

### 7. Jalankan Unit Tests

```bash
pytest tests/ -v
```

---

## 🔁 Alur Kerja Pipeline

### 1. FileWatcher
Memindai folder `input/` dan mengembalikan daftar file `.csv` atau `.json` yang siap diproses.

### 2. FileValidator
Melakukan validasi sebelum data diproses:
- Cek kolom wajib ada (`transaction_id`, `customer_id`, `amount`, dll)
- Cek nilai null di kolom kritis
- Cek nilai `status` hanya dari nilai yang diizinkan
- Cek `amount` tidak negatif

### 3. DataTransformer
Membersihkan dan menormalisasi data:
- Lowercase dan strip whitespace pada kolom teks
- Cast `amount` ke tipe numerik
- Cast `transaction_date` ke tipe datetime
- Hapus baris duplikat berdasarkan `transaction_id`

### 4. DataLoader
Melakukan **upsert** ke PostgreSQL:
- Jika `transaction_id` belum ada → **INSERT**
- Jika `transaction_id` sudah ada → **UPDATE**

### 5. File Management
- File berhasil → dipindahkan ke `archive/`
- File gagal validasi → dipindahkan ke `quarantine/`
- Semua proses dicatat ke `logs/pipeline_YYYYMMDD.log`

---

## ✅ Hasil Unit Test

```
pytest tests/ -v

tests/test_validator.py::test_valid_data_passes                  PASSED
tests/test_validator.py::test_missing_column_fails               PASSED
tests/test_validator.py::test_null_amount_fails                  PASSED
tests/test_validator.py::test_invalid_status_fails               PASSED
tests/test_transformer.py::test_transform_returns_dataframe      PASSED
tests/test_transformer.py::test_status_normalized_to_lowercase   PASSED
tests/test_transformer.py::test_customer_id_stripped             PASSED
tests/test_transformer.py::test_amount_cast_to_numeric           PASSED
tests/test_transformer.py::test_transaction_date_cast_to_datetime PASSED
tests/test_transformer.py::test_duplicates_removed               PASSED
tests/test_transformer.py::test_original_dataframe_not_modified  PASSED

11 passed in 0.45s
```

---

## 🧠 Konsep Clean Code yang Diterapkan

| Prinsip | Implementasi |
|---|---|
| **Single Responsibility** | Setiap file punya satu tanggung jawab: watcher, validator, transformer, loader terpisah |
| **Separation of Concerns** | Config, logic, dan orkestrasi dipisah sepenuhnya |
| **Idempotency** | Upsert memastikan pipeline aman dijalankan berulang kali |
| **Error Isolation** | File gagal dipindahkan ke quarantine, tidak menghentikan file lain |
| **Observability** | Logger otomatis mencatat setiap step ke file log harian |
| **Testability** | Setiap komponen bisa ditest secara independen dengan pytest |
| **Environment Config** | Semua credentials dari `.env`, tidak di-hardcode |

---

## 📋 Format File yang Didukung

| Format | Ekstensi |
|---|---|
| CSV | `.csv` |
| JSON | `.json` |

### Schema yang Diharapkan

| Kolom | Tipe | Wajib | Keterangan |
|---|---|---|---|
| `transaction_id` | string | ✅ | Primary key, harus unik |
| `customer_id` | string | ✅ | ID customer |
| `amount` | float | ✅ | Tidak boleh negatif |
| `transaction_date` | datetime | ✅ | Format: YYYY-MM-DD |
| `status` | string | ✅ | `completed`, `pending`, `failed`, `refunded` |

---

## 📊 Contoh Output Log

```
2024-01-15 10:00:00 [INFO]    — Pipeline dimulai
2024-01-15 10:00:00 [INFO]    — Ditemukan 2 file di input/
2024-01-15 10:00:00 [INFO]    — Memproses: transactions_2024_01.csv
2024-01-15 10:00:01 [INFO]    — Validasi BERHASIL
2024-01-15 10:00:01 [INFO]    — Transformasi selesai: 5 baris
2024-01-15 10:00:01 [INFO]    — Upsert 5 baris ke tabel transactions
2024-01-15 10:00:01 [INFO]    — Arsip: transactions_2024_01.csv → archive/
2024-01-15 10:00:01 [INFO]    — Memproses: transactions_invalid.csv
2024-01-15 10:00:02 [WARNING] — Validasi GAGAL: ['Kolom amount punya 2 nilai null']
2024-01-15 10:00:02 [WARNING] — Karantina: transactions_invalid.csv → quarantine/
2024-01-15 10:00:02 [INFO]    — Pipeline selesai — Berhasil: 1 | Gagal: 1
```

---

## 🗺️ Portofolio Data Engineering

| Project | Teknologi | Konsep |
|---|---|---|
| [ETL Pipeline - Web Scraping](#) | Python, BeautifulSoup | Extract, Web Scraping |
| [dbt Transformation Pipeline](#) | Python, PostgreSQL, dbt | Transform, Data Modeling |
| **Batch ETL Pipeline** | Python, PostgreSQL, pytest | Load, Validation, Error Handling |

---

## 👤 Author

**Nama Kamu**
- GitHub: [@username](https://github.com/username)
- LinkedIn: [linkedin.com/in/username](https://linkedin.com/in/username)
