from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import csv
import time

# ---------------- Chrome Options ----------------
options = webdriver.ChromeOptions()
options.add_argument("--headless=new")            # Headless mode
options.add_argument("--window-size=1920,1080")
options.add_argument("--disable-gpu")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--no-sandbox")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--log-level=3")
options.add_argument(
    "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)

# ---------------- Start driver -------------------
driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=options
)

url = (
    "https://pcsupport.lenovo.com/tc/en/products/laptops-and-netbooks/"
    "thinkpad-x-series-laptops/thinkpad-x1-carbon-13th-gen-type-21ns-21nt/"
    "downloads/driver-list/"
)
driver.get(url)
driver.set_window_size(1920, 1080)

# allow JS to settle
WebDriverWait(driver, 30).until(
    EC.presence_of_element_located((By.TAG_NAME, "body"))
)

# ---------------- Handle region popup ------------
try:
    proceed_button = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable(
            (By.XPATH, "//button[normalize-space()='Proceed with Turks and Caicos Islands']")
        )
    )
    driver.execute_script("arguments[0].click();", proceed_button)
    print("Clicked region popup")
except:
    print("Popup not found or not needed")

# ---------------- Click Audio tile ---------------
try:
    audio_tile = WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable(
            (By.XPATH, "//p[contains(normalize-space(),'Audio')]/ancestor::div[contains(@class,'tile')]")
        )
    )
    driver.execute_script("arguments[0].scrollIntoView(true);", audio_tile)
    time.sleep(1)
    driver.execute_script("arguments[0].click();", audio_tile)
    print("Clicked 'Audio' tile")
except:
    print("Audio tile not found")

# wait for table to render
time.sleep(6)
driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
time.sleep(2)

# ---------------- Extract data -------------------
soup = BeautifulSoup(driver.page_source, "html.parser")
rows = []

for row in soup.select("div.simple-table-dataRow"):
    content = row.select_one("div.table-body-content")
    version = row.select_one("span.table-version")
    if content:
        rows.append([content.get_text(strip=True),
                     version.get_text(strip=True) if version else ""])

# ---------------- Save CSV -----------------------
with open("lenovo_audio_content_version.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["Content", "Version"])
    writer.writerows(rows)

print(f"✅ Data saved to lenovo_audio_content_version.csv ({len(rows)} rows)")

driver.quit()
print("Finished.")
