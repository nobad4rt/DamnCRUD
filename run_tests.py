import os
import sys
import subprocess

def run_tests():
    """
    Menjalankan test secara paralel dengan pytest
    """
    print("Menjalankan integration testing dengan Selenium...")
    
    # Pastikan path Chrome driver sudah benar
    chrome_version = "134"  # Sesuaikan dengan versi Chrome Anda
    
    # Jalankan test dengan pytest
    command = [
        "pytest",
        "test_integration.py",
        "-v",                 # verbose output
        "--html=report.html", # generate HTML report
        "--self-contained-html",
        "-n", "2",            # run dengan 2 proses paralel (bisa disesuaikan)
    ]
    
    # Tampilkan command yang akan dijalankan
    print(f"Menjalankan command: {' '.join(command)}")
    
    # Jalankan pytest dengan subprocess
    result = subprocess.run(command, capture_output=True, text=True)
    
    # Tampilkan output
    print("\n--- OUTPUT PYTEST ---")
    print(result.stdout)
    
    if result.stderr:
        print("\n--- ERROR OUTPUT ---")
        print(result.stderr)
    
    # Tampilkan hasil
    if result.returncode == 0:
        print("\n✅ Semua test berhasil!")
    else:
        print(f"\n❌ Ada test yang gagal! (return code: {result.returncode})")
        print("Lihat report.html untuk detail lebih lanjut.")
    
    return result.returncode

if __name__ == "__main__":
    sys.exit(run_tests()) 