# Pengujian Keamanan Dinamis (DAST) untuk DamnCRUD

Dokumen ini menjelaskan cara kerja pengujian keamanan dinamis (DAST) yang telah diimplementasikan pada proyek DamnCRUD.

## Apa itu DAST?

Dynamic Application Security Testing (DAST) atau Pengujian Keamanan Aplikasi Dinamis adalah metodologi pengujian keamanan yang berfokus pada mengevaluasi aplikasi dari sisi eksternal tanpa pengetahuan tentang struktur internal kode aplikasi. DAST mensimulasikan serangan yang mungkin dilakukan peretas terhadap aplikasi yang sedang berjalan.

## Implementasi DAST di DamnCRUD

DamnCRUD menggunakan OWASP ZAP (Zed Attack Proxy) sebagai alat DAST utama. Pengujian ini dijalankan secara otomatis di dalam pipeline CI/CD GitHub Actions.

### Workflow DAST

Pengujian DAST dijalankan sebagai workflow terpisah (`dast-security-scan.yml`) yang akan dieksekusi setelah workflow integrasi utama selesai. Workflow ini melakukan:

1. **Persiapan Lingkungan**:
   - Menyiapkan PHP, MySQL, dan Apache
   - Mengkonfigurasi aplikasi DamnCRUD agar berjalan di lingkungan CI/CD

2. **Baseline Scan**:
   - Menggunakan OWASP ZAP Baseline Scan untuk mendeteksi kerentanan dasar
   - Menghasilkan laporan awal tentang kerentanan yang ditemukan

3. **Full Scan**:
   - Menggunakan OWASP ZAP Full Scan untuk pengujian yang lebih mendalam
   - Menghasilkan laporan lengkap tentang kerentanan yang ditemukan

### Konfigurasi Rules

Untuk mengurangi false positives dan memfokuskan pada kerentanan yang paling relevan, kami telah mengkonfigurasi aturan ZAP dalam file `.zap/rules.tsv`. Konfigurasi ini menentukan:

- Kerentanan yang diabaikan (IGNORE)
- Kerentanan yang diperhatikan sebagai peringatan (WARN)
- Kerentanan yang dianggap kritis (FAIL)

## Melihat Hasil DAST

Setelah workflow DAST selesai dijalankan, laporan hasil pengujian dapat diakses dari:

1. Tab "Actions" di repositori GitHub
2. Pilih workflow run "DAST Security Scan" yang telah selesai
3. Unduh artifact "zap-scan-reports" yang berisi laporan dalam format HTML dan Markdown

## Menjalankan DAST Secara Manual

Anda juga dapat menjalankan workflow DAST secara manual melalui:

1. Tab "Actions" di repositori GitHub 
2. Pilih workflow "DAST Security Scan"
3. Klik tombol "Run workflow"
4. Pilih branch yang ingin diuji dan klik "Run workflow"

## Memodifikasi Konfigurasi DAST

Jika ingin memodifikasi konfigurasi DAST:

1. Ubah file `.github/workflows/dast-security-scan.yml` untuk memodifikasi workflow
2. Ubah file `.zap/rules.tsv` untuk memodifikasi aturan ZAP

## Kerentanan yang Dipantau

Beberapa kerentanan utama yang dipantau oleh DAST termasuk:

- SQL Injection
- Cross-Site Scripting (XSS)
- Cross-Site Request Forgery (CSRF)
- Kerentanan autentikasi dan otorisasi
- Kesalahan konfigurasi keamanan
- Dan banyak lagi... 