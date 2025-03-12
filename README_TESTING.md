# Panduan Integration Testing untuk DamnCRUD

Dokumen ini menjelaskan cara menjalankan integration testing untuk aplikasi DamnCRUD.

## Prasyarat

Sebelum menjalankan integration test, pastikan Anda telah:

1. Menginstal PHP >= 7.3
2. Menginstal Composer
3. Menginstal database MySQL
4. Mengimpor struktur database dari file `db/damncrud.sql`
5. Mengkonfigurasi web server (Apache/Nginx) untuk menjalankan aplikasi ini
6. Menyesuaikan koneksi database di `functions.php` jika diperlukan

## Instalasi Dependensi

Jalankan perintah berikut untuk menginstal semua dependensi yang diperlukan:

```bash
composer install
```

## Konfigurasi

Sebelum menjalankan test, pastikan untuk menyesuaikan:

1. Alamat base URL di file `integration_test.php` sesuai dengan lingkungan lokal Anda:
   ```php
   protected $baseUrl = 'http://localhost/DamnCRUD'; // Sesuaikan dengan URL lokal Anda
   ```

2. Password untuk login di test jika berbeda:
   ```php
   'password' => 'password', // Sesuaikan dengan password yang benar
   ```

## Menjalankan Tests

Untuk menjalankan semua integration test, jalankan:

```bash
./vendor/bin/phpunit
```

Atau bisa juga menggunakan shortcut yang sudah dikonfigurasi di composer:

```bash
composer test
```

## Test Case yang Disertakan

Integration test mencakup skenario berikut:

1. **Autentikasi**
   - Login dengan kredensial valid
   - Login dengan kredensial tidak valid
   - Logout
   - Mencoba akses halaman tanpa login

2. **Operasi CRUD**
   - Melihat daftar kontak
   - Menambahkan kontak baru
   - Memperbarui kontak yang sudah ada
   - Menghapus kontak

## Troubleshooting

Jika test gagal, periksa:

1. Koneksi database - pastikan database dapat diakses dengan kredensial yang benar
2. URL aplikasi - pastikan aplikasi dapat diakses melalui URL yang dikonfigurasi
3. Versi PHP - pastikan menggunakan PHP 7.3 atau lebih tinggi
4. Kredensial login - pastikan username dan password yang digunakan dalam test sesuai dengan yang ada di database

## Catatan Penting

Test ini dirancang untuk berjalan pada lingkungan pengembangan, bukan lingkungan produksi. Jangan jalankan test ini pada database produksi karena akan mengubah data yang ada. 