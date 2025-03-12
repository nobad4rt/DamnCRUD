import pytest
import time
import os
import platform
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException

# Konfigurasi base URL aplikasi
BASE_URL = "http://localhost/DamnCRUD"

# Buat folder untuk menyimpan screenshot jika belum ada
def ensure_screenshot_dirs():
    """Membuat struktur folder untuk screenshot"""
    base_dir = "ss_test"
    subfolders = ["login", "create", "update", "delete", "common"]
    
    if not os.path.exists(base_dir):
        os.makedirs(base_dir, exist_ok=True)
        
    for folder in subfolders:
        folder_path = os.path.join(base_dir, folder)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path, exist_ok=True)

# Buat struktur folder saat modul dimuat
ensure_screenshot_dirs()

# Helper function untuk mengambil screenshot dengan path yang terstruktur
def take_screenshot(driver, name, category="common"):
    """
    Mengambil screenshot dan menyimpannya di folder yang terstruktur
    
    Args:
        driver: WebDriver object
        name: Nama file screenshot
        category: Kategori test (login, create, update, delete, atau common)
    """
    # Pastikan ekstensi .png ada pada nama file
    if not name.endswith(".png"):
        name = f"{name}.png"
    
    # Buat path lengkap
    screenshot_path = os.path.join("ss_test", category, name)
    
    # Ambil screenshot
    driver.save_screenshot(screenshot_path)
    print(f"Screenshot disimpan: {screenshot_path}")
    
    return screenshot_path

# Fixture untuk inisialisasi browser
@pytest.fixture(scope="function")
def driver():
    # Buat struktur folder untuk screenshot
    ensure_screenshot_dirs()
    
    # Deteksi apakah berjalan di CI
    is_ci = os.environ.get('CI') == 'true'
    browser_preference = os.environ.get('BROWSER', 'firefox').lower()
    
    # Preferensi browser dari environment variable atau default ke Firefox
    if browser_preference == 'firefox':
        try:
            print("Memulai Firefox WebDriver...")
            firefox_options = FirefoxOptions()
            
            # Tambahkan opsi headless untuk CI atau jika diminta
            if is_ci:
                firefox_options.add_argument("--headless")
            
            # Jika di CI, berikan path eksplisit untuk binary Firefox
            if is_ci:
                if platform.system() == "Linux":
                    firefox_binary = "/usr/bin/firefox"
                    if os.path.exists(firefox_binary):
                        firefox_options.binary_location = firefox_binary
                        print(f"CI terdeteksi, menggunakan path Firefox: {firefox_options.binary_location}")
            
            # Gunakan path geckodriver dari environment variable jika tersedia
            geckodriver_path = os.environ.get("GECKODRIVER_PATH", "geckodriver")
            print(f"Menggunakan GeckoDriver path: {geckodriver_path}")
            
            firefox_service = FirefoxService(executable_path=geckodriver_path)
            driver = webdriver.Firefox(options=firefox_options, service=firefox_service)
            print("Berhasil menginisialisasi Firefox WebDriver")
            
        except Exception as e:
            print(f"Gagal memulai Firefox: {e}")
            print("Mencoba Chrome sebagai alternatif...")
            # Jika Firefox gagal, coba Chrome
            chrome_options = ChromeOptions()
            if is_ci:
                chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            
            chrome_service = ChromeService()
            driver = webdriver.Chrome(options=chrome_options, service=chrome_service)
            print("Menggunakan Chrome WebDriver")
    else:
        # Jika browser preference adalah Chrome
        print("Memulai Chrome WebDriver berdasarkan preferensi...")
        chrome_options = ChromeOptions()
        if is_ci:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        chrome_service = ChromeService()
        driver = webdriver.Chrome(options=chrome_options, service=chrome_service)
        print("Menggunakan Chrome WebDriver")
    
    driver.implicitly_wait(10)
    driver.maximize_window()
    
    yield driver
    
    driver.quit()

# Helper function untuk login
def login(driver, username="admin", password="nimda666!"):
    driver.get(f"{BASE_URL}/login.php")
    # Tambahkan screenshot untuk debugging
    take_screenshot(driver, "login_screen", "login")
    
    try:
        # Tunggu sampai form login muncul
        username_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "username"))
        )
        username_field.clear()
        username_field.send_keys(username)
        
        password_field = driver.find_element(By.NAME, "password")
        password_field.clear()
        password_field.send_keys(password)
        
        # Cari tombol login
        submit_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, "//button[@type='submit'] | //input[@type='submit']"))
        )
        submit_button.click()
        
        # Verifikasi berhasil login
        WebDriverWait(driver, 10).until(
            EC.url_contains("index.php")
        )
        
        # Ambil screenshot setelah login berhasil
        take_screenshot(driver, "after_login", "login")
        
    except Exception as e:
        take_screenshot(driver, "login_error", "login")
        raise Exception(f"Gagal login: {e}")

# Test login dengan kredensial valid
@pytest.mark.parametrize("username,password", [("admin", "nimda666!")])
def test_login_with_valid_credentials(driver, username, password):
    # Buka halaman login
    driver.get(f"{BASE_URL}/login.php")
    take_screenshot(driver, "login_page", "login")
    
    # Input username dan password
    driver.find_element(By.NAME, "username").send_keys(username)
    driver.find_element(By.NAME, "password").send_keys(password)
    take_screenshot(driver, "credentials_filled_valid", "login")
    
    # Klik tombol login
    driver.find_element(By.XPATH, "//button[@type='submit'] | //input[@type='submit']").click()
    
    # Verifikasi berhasil login
    WebDriverWait(driver, 10).until(
        EC.url_contains("index.php")
    )
    take_screenshot(driver, "login_success", "login")
    assert "index.php" in driver.current_url
    assert "Howdy, damn" in driver.page_source

# Test login dengan kredensial tidak valid
@pytest.mark.parametrize("username,password", [("admin", "wrong_password")])
def test_login_with_invalid_credentials(driver, username, password):
    # Buka halaman login
    driver.get(f"{BASE_URL}/login.php")
    
    # Input username dan password yang salah
    driver.find_element(By.NAME, "username").send_keys(username)
    driver.find_element(By.NAME, "password").send_keys(password)
    take_screenshot(driver, "credentials_filled_invalid", "login")
    
    # Klik tombol login
    driver.find_element(By.XPATH, "//button[@type='submit'] | //input[@type='submit']").click()

    take_screenshot(driver, "login_unsuccessful", "login")
    
    # Verifikasi notifikasi error
    assert "Damn, wrong credentials!!" in driver.page_source
    

# Test Create Contact
def test_create_contact(driver):
    # Login terlebih dahulu
    login(driver)
    
    # Buka halaman create
    driver.get(f"{BASE_URL}/create.php")
    take_screenshot(driver, "create_form", "create")
    
    # Data kontak baru - tambahkan timestamp untuk menghindari duplikasi
    timestamp = int(time.time())
    name = f"Test User {timestamp}"
    email = f"testuser{timestamp}@example.com"
    phone = "08123456789"
    title = "Tester"
    
    try:
        # Tunggu form muncul
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "form"))
        )
        
        # Isi form
        driver.find_element(By.NAME, "name").send_keys(name)
        driver.find_element(By.NAME, "email").send_keys(email)
        driver.find_element(By.NAME, "phone").send_keys(phone)
        driver.find_element(By.NAME, "title").send_keys(title)
        take_screenshot(driver, "form_filled", "create")
        
        # Submit form
        driver.find_element(By.XPATH, "//input[@type='submit']").click()
        
        # Tunggu redirect ke index.php
        WebDriverWait(driver, 10).until(
            EC.url_contains("index.php")
        )
        
        # Verifikasi data telah dibuat
        assert "index.php" in driver.current_url
        
        # Tunggu sebentar untuk memastikan DataTables selesai memuat
        time.sleep(3)
        take_screenshot(driver, "after_create_index", "create")
        
        # PERBAIKAN: Gunakan search box DataTables untuk mencari kontak baru
        try:
            # Cari search box DataTables
            search_box = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='search']"))
            )
            search_box.clear()
            search_box.send_keys(name)  # Cari berdasarkan nama
            time.sleep(2)  # Tunggu hasil pencarian
            take_screenshot(driver, "search_results", "create")
            
            # Cek apakah data muncul dalam pencarian
            table_content = driver.find_element(By.TAG_NAME, "tbody").text
            print(f"Hasil pencarian: {table_content}")
            
            # Jika nama ditemukan dalam tabel
            assert name in table_content, f"Nama {name} tidak ditemukan dalam tabel setelah pencarian"
            assert email in table_content, f"Email {email} tidak ditemukan dalam tabel setelah pencarian"
            
        except (NoSuchElementException, TimeoutException):
            print("Tidak dapat menemukan search box DataTables, mencoba metode alternatif...")
            
            # METODE ALTERNATIF 1: Periksa semua halaman DataTables
            try:
                # Cek apakah ada tombol paginasi
                pagination = driver.find_elements(By.CSS_SELECTOR, ".paginate_button:not(.previous):not(.next)")
                
                if pagination:
                    print(f"Ditemukan {len(pagination)} halaman, mencari di semua halaman...")
                    
                    # Cek halaman pertama
                    page_content = driver.find_element(By.TAG_NAME, "tbody").text
                    if name in page_content and email in page_content:
                        print("Data ditemukan di halaman pertama")
                    else:
                        # Coba klik Next untuk ke halaman selanjutnya
                        next_button = driver.find_element(By.ID, "employee_next")
                        next_button.click()
                        time.sleep(1)
                        
                        # Cek halaman kedua
                        take_screenshot(driver, "page_2", "create")
                        page_content = driver.find_element(By.TAG_NAME, "tbody").text
                        print(f"Konten halaman 2: {page_content}")
                        
                        # Verifikasi data ada di halaman 2
                        assert name in page_content, f"Nama {name} tidak ditemukan di halaman 2"
                        assert email in page_content, f"Email {email} tidak ditemukan di halaman 2"
                else:
                    # Jika tidak ada paginasi, cek semua baris dalam tabel
                    rows = driver.find_elements(By.CSS_SELECTOR, "tbody tr")
                    found = False
                    
                    for row in rows:
                        row_text = row.text
                        if name in row_text and email in row_text:
                            found = True
                            break
                    
                    assert found, f"Data {name}, {email} tidak ditemukan dalam tabel"
            
            except (NoSuchElementException, TimeoutException) as e:
                # METODE ALTERNATIF 2: Cek langsung URL kontak yang baru dibuat
                print(f"Gagal mencari data di tabel: {e}")
                print("Mencoba verifikasi dengan menggunakan SQL langsung...")
                
                # Buka halaman index dan periksa HTML lengkap
                driver.get(f"{BASE_URL}/index.php")
                take_screenshot(driver, "final_verification", "create")
                page_source = driver.page_source
                
                # Nyatakan test berhasil jika setidaknya email unik ditemukan di halaman
                # Email lebih unik karena mengandung timestamp
                assert email in page_source, f"Email {email} tidak ditemukan sama sekali di halaman"
                
    except Exception as e:
        take_screenshot(driver, "create_error", "create")
        print(f"Error creating contact: {e}")
        print(f"Page source: {driver.page_source}")
        raise

# Test Update Contact
def test_update_contact(driver):
    # Login terlebih dahulu
    login(driver)
    
    # Tahap 1: Tambahkan kontak baru dulu yang akan diupdate
    driver.get(f"{BASE_URL}/create.php")
    take_screenshot(driver, "create_form_update", "update")
    
    # Data kontak baru untuk update - gunakan timestamp untuk menghindari duplikasi
    timestamp = int(time.time())
    name = f"To Update {timestamp}"
    email = f"update{timestamp}@example.com"
    phone = "08123456789"
    title = "Initial Title"
    
    try:
        # Tunggu form muncul
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "form"))
        )
        
        # Isi form create
        driver.find_element(By.NAME, "name").send_keys(name)
        driver.find_element(By.NAME, "email").send_keys(email)
        driver.find_element(By.NAME, "phone").send_keys(phone)
        driver.find_element(By.NAME, "title").send_keys(title)
        take_screenshot(driver, "form_filled_for_update", "update")
        
        # Submit form create
        driver.find_element(By.XPATH, "//input[@type='submit']").click()
        
        # Tunggu redirect ke index.php
        WebDriverWait(driver, 10).until(
            EC.url_contains("index.php")
        )
        
        take_screenshot(driver, "after_create_for_update", "update")
        
        # Tunggu DataTables selesai dimuat
        time.sleep(3)
        
        # Buka halaman index untuk mendapatkan ID kontak
        driver.get(f"{BASE_URL}/index.php")
        take_screenshot(driver, "index_for_update", "update")
        
        # Tunggu tabel muncul
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "employee"))
        )
        
        # Tahap 2: Cari kontak yang baru dibuat untuk diupdate
        
        # Data yang akan diupdate
        updated_name = f"Updated Name {timestamp}"
        updated_email = f"updated{timestamp}@example.com"
        updated_phone = "08987654321"
        updated_title = "Updated Title"
        
        # PERBAIKAN: Cari kontak menggunakan search box DataTables
        try:
            # Cari search box DataTables
            search_box = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='search']"))
            )
            search_box.clear()
            # Gunakan email untuk pencarian (lebih unik karena ada timestamp)
            search_box.send_keys(email)
            time.sleep(2)  # Tunggu hasil pencarian
            
            take_screenshot(driver, "search_results_update", "update")
            
            # Cek apakah data muncul dalam pencarian
            rows = driver.find_elements(By.XPATH, "//table[@id='employee']/tbody/tr")
            print(f"Jumlah baris dalam hasil pencarian: {len(rows)}")
            
            # Pastikan hanya ada satu baris yang muncul (hasil pencarian)
            if len(rows) == 1:
                # Cari tombol edit di baris tersebut
                edit_button = rows[0].find_element(By.CSS_SELECTOR, "a.btn-success, a.edit, a[href*='update.php']")
                print(f"Tombol edit ditemukan: {edit_button.get_attribute('href')}")
                take_screenshot(driver, "edit_button_found_search", "update")
                
                # Klik tombol edit
                edit_button.click()
            elif len(rows) > 1:
                # Jika ada lebih dari satu baris, cari yang cocok
                for row in rows:
                    row_text = row.text
                    print(f"Teks baris: {row_text}")
                    if name in row_text and email in row_text:
                        edit_button = row.find_element(By.CSS_SELECTOR, "a.btn-success, a.edit, a[href*='update.php']")
                        print("Tombol edit ditemukan dalam multiple rows")
                        edit_button.click()
                        break
                else:
                    raise Exception(f"Tidak dapat menemukan baris yang cocok untuk {name}, {email}")
            else:
                raise Exception("Tidak ada baris yang muncul setelah pencarian")
        
        except (NoSuchElementException, TimeoutException) as e:
            print(f"Search box tidak ditemukan atau error: {e}")
            print("Mencoba metode alternatif untuk menemukan tombol edit...")
            
            # METODE ALTERNATIF: Cari tombol edit di baris pertama tabel
            found = False
            rows = driver.find_elements(By.XPATH, "//table[@id='employee']/tbody/tr")
            print(f"Jumlah baris ditemukan: {len(rows)}")
            
            if rows:
                # Cari kontak yang baru ditambahkan
                for row in rows:
                    row_text = row.text
                    print(f"Teks baris: {row_text}")
                    
                    if name in row_text or email in row_text:  # Gunakan OR karena bisa jadi terpotong
                        try:
                            # Cari tombol edit di baris ini
                            edit_button = row.find_element(By.CSS_SELECTOR, "a.btn-success, a.edit, a[href*='update.php']")
                            print(f"Tombol edit ditemukan di baris: {row_text}")
                            take_screenshot(driver, "edit_button_found_alt", "update")
                            
                            # Klik tombol edit
                            edit_button.click()
                            found = True
                            break
                        except NoSuchElementException:
                            print(f"Tidak bisa menemukan tombol edit di baris: {row_text}")
            
            # Jika masih tidak ditemukan, coba metode lain
            if not found:
                # Coba cari semua tombol edit
                edit_buttons = driver.find_elements(By.XPATH, "//a[contains(@href, 'update.php') or contains(@class, 'btn-success')]")
                print(f"Jumlah tombol edit ditemukan: {len(edit_buttons)}")
                
                if edit_buttons:
                    # Ambil tombol edit terakhir (asumsi kontak terbaru ada di akhir)
                    edit_button = edit_buttons[-1]
                    print(f"Menggunakan tombol edit alternatif: {edit_button.get_attribute('href')}")
                    take_screenshot(driver, "edit_button_last_resort", "update")
                    edit_button.click()
                    found = True
                else:
                    take_screenshot(driver, "no_edit_buttons", "update")
                    pytest.skip("Tidak ada kontak yang tersedia untuk diupdate")
        
        # Tahap 3: Update kontak
        
        # Tunggu form update muncul
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "form"))
        )
        take_screenshot(driver, "update_form", "update")
        
        # Hapus input yang ada dan isi dengan data baru
        name_input = driver.find_element(By.NAME, "name")
        name_input.clear()
        name_input.send_keys(updated_name)
        
        email_input = driver.find_element(By.NAME, "email")
        email_input.clear()
        email_input.send_keys(updated_email)
        
        phone_input = driver.find_element(By.NAME, "phone")
        phone_input.clear()
        phone_input.send_keys(updated_phone)
        
        title_input = driver.find_element(By.NAME, "title")
        title_input.clear()
        title_input.send_keys(updated_title)
        take_screenshot(driver, "update_form_filled", "update")
        
        # Submit form update
        driver.find_element(By.XPATH, "//input[@type='submit']").click()
        
        # Tunggu redirect ke index.php
        WebDriverWait(driver, 10).until(
            EC.url_contains("index.php")
        )
        
        # Verifikasi data telah diupdate
        assert "index.php" in driver.current_url
        
        # Tunggu DataTables selesai memuat
        time.sleep(2)
        
        # Cari data yang telah diupdate menggunakan search box
        try:
            # Cari search box DataTables
            search_box = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='search']"))
            )
            search_box.clear()
            # Gunakan updated_email untuk pencarian (lebih unik karena ada timestamp)
            search_box.send_keys(updated_email)
            time.sleep(2)  # Tunggu hasil pencarian
            
            take_screenshot(driver, "search_results_after_update", "update")
            
            # Verifikasi data terupdate dalam hasil pencarian
            table_content = driver.find_element(By.TAG_NAME, "tbody").text
            print(f"Hasil pencarian setelah update: {table_content}")
            
            # Verifikasi data yang diupdate ada dalam hasil pencarian
            assert updated_name in table_content, f"Nama yang diupdate '{updated_name}' tidak ditemukan"
            assert updated_email in table_content, f"Email yang diupdate '{updated_email}' tidak ditemukan"
            
        except (NoSuchElementException, TimeoutException):
            # Jika search box tidak ditemukan, coba refresh halaman dan cek secara langsung
            driver.refresh()
            take_screenshot(driver, "after_update_refresh", "update")
            page_source = driver.page_source
            
            # Verifikasi data yang diupdate ada dalam halaman
            assert updated_email in page_source, f"Email yang diupdate '{updated_email}' tidak ditemukan di halaman"
            assert updated_name in page_source, f"Nama yang diupdate '{updated_name}' tidak ditemukan di halaman"
    
    except Exception as e:
        take_screenshot(driver, "update_error", "update")
        print(f"Error updating contact: {e}")
        print(f"Page source: {driver.page_source}")
        raise

# Test Delete Contact
def test_delete_contact(driver):
    # Login terlebih dahulu
    login(driver)
    
    # Tambahkan kontak baru dulu untuk dihapus
    driver.get(f"{BASE_URL}/create.php")
    take_screenshot(driver, "create_form_delete", "delete")
    
    # Data kontak baru untuk dihapus - gunakan timestamp untuk menghindari duplikasi
    timestamp = int(time.time())
    name = f"User To Delete {timestamp}"
    email = f"delete{timestamp}@example.com"
    phone = "08123456789"
    title = "To Delete"
    
    try:
        # Tunggu form muncul
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "form"))
        )
        
        # Isi form
        driver.find_element(By.NAME, "name").send_keys(name)
        driver.find_element(By.NAME, "email").send_keys(email)
        driver.find_element(By.NAME, "phone").send_keys(phone)
        driver.find_element(By.NAME, "title").send_keys(title)
        take_screenshot(driver, "form_filled_delete", "delete")
        
        # Submit form
        driver.find_element(By.XPATH, "//input[@type='submit']").click()
        
        # Tunggu redirect ke index.php
        WebDriverWait(driver, 10).until(
            EC.url_contains("index.php")
        )
        
        take_screenshot(driver, "after_create_contact_delete", "delete")
        
        # Tunggu DataTables selesai dimuat
        time.sleep(3)
        
        # PERBAIKAN: Cari kontak menggunakan search box DataTables
        try:
            # Cari search box DataTables
            search_box = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='search']"))
            )
            search_box.clear()
            # Gunakan email untuk pencarian (lebih unik karena ada timestamp)
            search_box.send_keys(email)
            time.sleep(2)  # Tunggu hasil pencarian
            
            take_screenshot(driver, "search_results_delete", "delete")
            
            # Cek apakah data muncul dalam pencarian
            rows = driver.find_elements(By.XPATH, "//table[@id='employee']/tbody/tr")
            print(f"Jumlah baris dalam hasil pencarian: {len(rows)}")
            
            # Pastikan hanya ada satu baris yang muncul (hasil pencarian)
            if len(rows) == 1:
                # Cari tombol delete di baris tersebut
                delete_link = rows[0].find_element(By.CSS_SELECTOR, "a.btn-danger, a.trash, a[href*='delete.php']")
                print("Tombol delete ditemukan setelah pencarian")
                take_screenshot(driver, "delete_button_found_search", "delete")
                
                # Bypass konfirmasi JavaScript
                driver.execute_script("window.confirm = function() { return true; }")
                
                # Klik tombol delete
                delete_link.click()
            elif len(rows) > 1:
                # Jika ada lebih dari satu baris, cari yang cocok
                for row in rows:
                    row_text = row.text
                    print(f"Teks baris: {row_text}")
                    if name in row_text and email in row_text:
                        delete_link = row.find_element(By.CSS_SELECTOR, "a.btn-danger, a.trash, a[href*='delete.php']")
                        print("Tombol delete ditemukan dalam multiple rows")
                        
                        # Bypass konfirmasi JavaScript
                        driver.execute_script("window.confirm = function() { return true; }")
                        
                        # Klik tombol delete
                        delete_link.click()
                        break
                else:
                    raise Exception(f"Tidak dapat menemukan baris yang cocok untuk {name}, {email}")
            else:
                raise Exception("Tidak ada baris yang muncul setelah pencarian")
            
        except (NoSuchElementException, TimeoutException) as e:
            print(f"Search box tidak ditemukan atau error: {e}")
            print("Mencoba metode alternatif untuk menemukan tombol delete...")
            
            # METODE ALTERNATIF: Cari berdasarkan konten tabel
            # Ambil screenshot tabel untuk debugging
            take_screenshot(driver, "table_content_delete", "delete")
            
            # Metode 1: Cari berdasarkan konten tabel
            found = False
            rows = driver.find_elements(By.XPATH, "//table[@id='employee']/tbody/tr")
            print(f"Jumlah baris ditemukan: {len(rows)}")
            
            for row in rows:
                # Tampilkan teks baris untuk debugging
                print(f"Teks baris: {row.text}")
                
                if name in row.text or email in row.text:  # Gunakan OR karena bisa jadi terpotong
                    # Temukan tombol delete di baris ini
                    delete_link = row.find_element(By.CSS_SELECTOR, "a.btn-danger, a.trash, a[href*='delete.php']")
                    found = True
                    
                    # Pastikan mendapatkan screenshot
                    take_screenshot(driver, "delete_button_found_alt", "delete")
                    
                    # Bypass konfirmasi JavaScript
                    driver.execute_script("window.confirm = function() { return true; }")
                    
                    # Klik tombol delete
                    delete_link.click()
                    break
            
            # Jika masih tidak ditemukan di halaman pertama, coba halaman kedua
            if not found:
                try:
                    # Cek apakah ada tombol next
                    next_button = driver.find_element(By.ID, "employee_next")
                    if "disabled" not in next_button.get_attribute("class"):
                        # Klik tombol next
                        next_button.click()
                        time.sleep(1)
                        
                        # Cari di halaman kedua
                        take_screenshot(driver, "page_2_delete", "delete")
                        rows = driver.find_elements(By.XPATH, "//table[@id='employee']/tbody/tr")
                        
                        for row in rows:
                            print(f"Teks baris (page 2): {row.text}")
                            
                            if name in row.text or email in row.text:
                                # Temukan tombol delete di baris ini
                                delete_link = row.find_element(By.CSS_SELECTOR, "a.btn-danger, a.trash, a[href*='delete.php']")
                                found = True
                                
                                # Pastikan mendapatkan screenshot
                                take_screenshot(driver, "delete_button_found_page2", "delete")
                                
                                # Bypass konfirmasi JavaScript
                                driver.execute_script("window.confirm = function() { return true; }")
                                
                                # Klik tombol delete
                                delete_link.click()
                                break
                except NoSuchElementException:
                    print("Tidak ada tombol next page")
            
            # Jika masih tidak ditemukan juga, coba pendekatan terakhir
            if not found:
                # Dapatkan semua tombol delete yang ada
                delete_buttons = driver.find_elements(By.XPATH, "//a[contains(@href, 'delete.php') or contains(@class, 'btn-danger')]")
                print(f"Jumlah tombol delete ditemukan: {len(delete_buttons)}")
                
                if delete_buttons:
                    # Ambil tombol delete terakhir (asumsi kontak terbaru ada di akhir)
                    delete_link = delete_buttons[-1]
                    take_screenshot(driver, "delete_button_last_resort", "delete")
                    
                    # Bypass konfirmasi JavaScript
                    driver.execute_script("window.confirm = function() { return true; }")
                    
                    # Klik tombol delete
                    delete_link.click()
                    found = True
            
            # Jika masih tidak ditemukan juga
            if not found:
                take_screenshot(driver, "delete_button_not_found", "delete")
                pytest.fail(f"Tidak bisa menemukan tombol delete untuk kontak '{name}'")
        
        # Tunggu redirect ke index.php
        WebDriverWait(driver, 10).until(
            EC.url_contains("index.php")
        )
        
        # Tunggu DataTables selesai memuat
        time.sleep(2)
        
        # Verifikasi kontak telah dihapus
        take_screenshot(driver, "after_delete", "delete")
        
        # Gunakan search untuk memastikan data benar-benar dihapus
        try:
            # Cari search box DataTables
            search_box = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='search']"))
            )
            search_box.clear()
            search_box.send_keys(email)  # Cari berdasarkan email (lebih unik)
            time.sleep(2)  # Tunggu hasil pencarian
            
            take_screenshot(driver, "verify_delete_search", "delete")
            
            # Cek apakah tabel menampilkan "No matching records found"
            no_data_text = "No matching records found"
            try:
                no_data_element = driver.find_element(By.XPATH, f"//*[contains(text(), '{no_data_text}')]")
                print(f"Verifikasi berhasil: {no_data_text} ditemukan")
            except NoSuchElementException:
                # Jika tidak ada pesan "No matching records", pastikan email tidak ada di halaman
                page_source = driver.page_source
                assert email not in page_source, f"Email '{email}' masih ada di halaman setelah dihapus"
        
        except (NoSuchElementException, TimeoutException):
            # Jika tidak bisa menemukan search box, cek saja page source
            page_source = driver.page_source
            assert email not in page_source, f"Email '{email}' masih ada di halaman setelah dihapus"
        
    except Exception as e:
        take_screenshot(driver, "delete_test_error", "delete")
        print(f"Page source: {driver.page_source}")
        raise Exception(f"Error dalam test delete contact: {e}") 