from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import csv
import time

# ---------- Browser Setup ----------
options = webdriver.ChromeOptions()
options.add_argument("--headless=new")  # Headless mode
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

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
driver.get(
    "https://pcsupport.lenovo.com/tc/en/products/laptops-and-netbooks/"
    "thinkpad-x-series-laptops/thinkpad-x1-carbon-13th-gen-type-21ns-21nt/"
    "downloads/driver-list/"
)

wait = WebDriverWait(driver, 30)
wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))

# ---------- Handle Region Popup ----------
try:
    proceed = wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, "//button[normalize-space()='Proceed with Turks and Caicos Islands']")
        )
    )
    driver.execute_script("arguments[0].click();", proceed)
    print("Region popup clicked")
except:
    print("Region popup not found/needed")

# ---------- Function to scrape driver table ----------
def scrape_current_table():
    """Scrape driver name/content + version from current page."""
    time.sleep(5)  # wait for table to load
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(1)
    soup = BeautifulSoup(driver.page_source, "html.parser")
    rows = []
    for row in soup.select("div.simple-table-dataRow"):
        content = row.select_one("div.table-body-content")
        version = row.select_one("span.table-version")
        if content:
            rows.append([
                content.get_text(strip=True),
                version.get_text(strip=True) if version else ""
            ])
    return rows

# ---------- CSV Setup ----------
csv_file = "lenovo_drivers.csv"
with open(csv_file, "w", newline="", encoding="utf-8") as f:
    csv.writer(f).writerow(["Content", "Version"])

# ---------- Categories and XPaths ----------
categories_to_scrape = [
    "audio", "bluetooth", "video", "advanced_firmware", "bios", "camera",
    "diagnostic", "enterprise_management", "fingerprint", "motherboard",
    "keyboard_mouse_pen", "wireless_lan", "wireless_wan", "power_management",
    "software", "storage", "thinkvantage_technology"
]

category_xpaths = {
    "audio": "//p[contains(translate(normalize-space(),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'audio')]/ancestor::div[contains(@class,'tile')]",
    "bluetooth": "//p[contains(translate(normalize-space(),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'bluetooth')]/ancestor::div[contains(@class,'tile')]",
    "video": "//span[contains(@class,'dl-category-video')]/ancestor::div[contains(@class,'icon')]",
    "advanced_firmware": "(//span[contains(@class,'dl-category-bios')]/ancestor::div[contains(@class,'icon')])[1]",
    "bios": "(//span[contains(@class,'dl-category-bios')]/ancestor::div[contains(@class,'icon')])[2]",
    "camera": "//span[contains(@class,'dl-category-camerareader')]/ancestor::div[contains(@class,'icon')]",
    "diagnostic": "//span[contains(@class,'dl-category-diags')]/ancestor::div[contains(@class,'icon')]",
    "enterprise_management": "//span[contains(@class,'dl-category-enterprise')]/ancestor::div[contains(@class,'icon')]",
    "fingerprint": "//span[contains(@class,'dl-category-fingerprint')]/ancestor::div[contains(@class,'icon')]",
    "motherboard": "//span[contains(@class,'dl-category-chipset')]/ancestor::div[contains(@class,'icon')]",
    "keyboard_mouse_pen": "//span[contains(@class,'dl-category-keyboard')]/ancestor::div[contains(@class,'icon')]",
    "wireless_lan": "//span[contains(@class,'dl-category-Wifi')]/ancestor::div[contains(@class,'icon')]",
    "wireless_wan": "//span[contains(@class,'dl-category-wan')]/ancestor::div[contains(@class,'icon')]",
    "power_management": "//span[contains(@class,'dl-category-powermgmt')]/ancestor::div[contains(@class,'icon')]",
    "software": "//span[contains(@class,'dl-category-software')]/ancestor::div[contains(@class,'icon')]",
    "storage": "//span[contains(@class,'dl-category-storage')]/ancestor::div[contains(@class,'icon')]",
    "thinkvantage_technology": "//span[contains(@class,'dl-category-thinkvantage')]/ancestor::div[contains(@class,'icon')]"
}

# ---------- Loop through categories ----------
for category in categories_to_scrape:
    try:
        print(f"\n📌 Processing category: {category}")
        tile_xpath = category_xpaths.get(category)
        if not tile_xpath:
            print(f"❌ No XPath defined for category '{category}'")
            continue

        # Wait for tile visibility, scroll, then click
        tile_element = WebDriverWait(driver, 30).until(
            EC.visibility_of_element_located((By.XPATH, tile_xpath))
        )
        driver.execute_script(
            "arguments[0].scrollIntoView({behavior:'smooth', block:'center'});", tile_element
        )
        time.sleep(0.7)
        driver.execute_script("arguments[0].click();", tile_element)
        print(f"✅ Clicked '{category}' tile (headless-safe)")

        # Scrape table data
        rows = scrape_current_table()
        if rows:
            with open(csv_file, "a", newline="", encoding="utf-8") as f:
                csv.writer(f).writerows(rows)
            print(f"✅ {category.capitalize()} data appended ({len(rows)} rows)")
        else:
            print(f"⚠️ No data found for {category}")

        # Return to main driver list
        driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(1)
        driver.execute_script("window.history.go(-1)")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        time.sleep(1)

    except Exception as e:
        print(f"❌ Failed to process category '{category}': {e}")
        continue

driver.quit()
print(f"\nFinished. All data stored in {csv_file}")
