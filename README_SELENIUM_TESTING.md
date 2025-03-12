# Pengujian Integrasi DamnCRUD dengan Selenium dan GitHub Actions

Dokumen ini berisi instruksi untuk menjalankan pengujian integrasi aplikasi DamnCRUD menggunakan Selenium WebDriver dengan Python dan pytest, serta cara mengatur pipeline CI/CD di GitHub Actions.

## Struktur Pengujian

Pengujian integrasi ini terdiri dari:

1. **Test Login**
   - Login dengan kredensial valid
   - Login dengan kredensial tidak valid

2. **Test CRUD**
   - Membuat kontak baru (Create)
   - Memperbarui kontak yang ada (Update)
   - Menghapus kontak (Delete)

## Prasyarat untuk Menjalankan Pengujian Lokal

- Python 3.8 atau lebih tinggi
- Pip (Python package manager)
- Google Chrome browser
- ChromeDriver (diinstal otomatis oleh webdriver-manager)
- Web server (Apache/XAMPP/WAMP) untuk menjalankan aplikasi PHP
- Database MySQL

## Instalasi Dependensi

Jalankan perintah berikut untuk menginstal semua dependensi Python yang diperlukan:

```bash
pip install -r requirements.txt
```

## Menjalankan Pengujian Lokal

Sebelum menjalankan pengujian, pastikan:

1. Aplikasi DamnCRUD sudah diinstal di web server lokal
2. Database MySQL sudah diimport dari file `db/damncrud.sql`
3. Sesuaikan BASE_URL di `test_integration.py` jika diperlukan

Untuk menjalankan pengujian:

```bash
# Menjalankan semua test
pytest

# Menjalankan secara paralel
pytest -n auto

# Menjalankan test tertentu
pytest test_integration.py::test_login_with_valid_credentials
```

## GitHub Actions CI/CD Pipeline

Pengujian integrasi ini dikonfigurasi untuk berjalan otomatis di GitHub Actions. Berikut alur kerjanya:

1. Trigger: Pipeline akan berjalan saat push ke branch main/master, saat pull request, atau secara manual
2. Setup: Menginstal PHP, MySQL, Apache, Chrome, dan dependensi Python
3. Pengujian: Menjalankan test dengan Selenium secara paralel
4. Laporan: Menghasilkan dan menyimpan laporan HTML hasil pengujian

Untuk melihat hasil pengujian:
1. Buka tab "Actions" di repositori GitHub
2. Pilih workflow run terbaru
3. Di bagian "Artifacts", unduh "test-reports"

## Menyesuaikan Pengujian

### Konfigurasi Paralel

Untuk menyesuaikan jumlah proses paralel, ubah parameter `-n` di file `pytest.ini` atau saat menjalankan perintah pytest.

### Menambahkan Test Case

Untuk menambahkan test case baru:

1. Tambahkan fungsi baru di `test_integration.py` dengan nama yang dimulai dengan `test_`
2. Gunakan fixture `driver` untuk mengakses browser
3. Jika diperlukan, tambahkan marker baru di `pytest.ini`

## Troubleshooting

### Pengujian Gagal di GitHub Actions

1. Periksa log build di GitHub Actions untuk pesan error
2. Pastikan konfigurasi database di workflow file sesuai dengan skema database
3. Periksa apakah ada perubahan struktur HTML yang memengaruhi selectors Selenium

### Pengujian Gagal di Lokal

1. Pastikan web server dan MySQL berjalan
2. Periksa koneksi database di `functions.php`
3. Pastikan ChromeDriver kompatibel dengan versi Chrome yang diinstal 