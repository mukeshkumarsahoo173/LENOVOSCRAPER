from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import csv
import time

# ---------------- Chrome setup ----------------
options = webdriver.ChromeOptions()
options.add_argument("--disable-gpu")
options.add_argument("--disable-software-rasterizer")
options.add_argument("--no-sandbox")
# options.add_argument("--headless")  # Keep OFF to see browser

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# ---------------- Open Lenovo driver page ----------------
url = "https://pcsupport.lenovo.com/tc/en/products/laptops-and-netbooks/thinkpad-x-series-laptops/thinkpad-x1-carbon-13th-gen-type-21ns-21nt/downloads/driver-list/"
driver.get(url)
time.sleep(3)  # wait for page to load

# ---------------- Click popup if present ----------------
try:
    proceed_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//button[text()='Proceed with Turks and Caicos Islands']"))
    )
    proceed_button.click()
    print("Clicked 'Proceed with Turks and Caicos Islands'")
except:
    print("Popup not found")

time.sleep(2)

# ---------------- Click Audio (2) tile ----------------
try:
    audio_tile = WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.XPATH, "//p[contains(text(),'Audio (2)')]/ancestor::div[@class='tile']"))
    )
    driver.execute_script("arguments[0].click();", audio_tile)
    print("Clicked 'Audio (2)' tile via JS")
except:
    print("Audio (2) tile not found")

time.sleep(3)  # wait for table to render

# ---------------- Extract table-body-content spans ----------------
soup = BeautifulSoup(driver.page_source, "html.parser")
rows = soup.find_all("div", class_="simple-table-dataRow")

data_list = []
for row in rows:
    # Content span
    content_span = row.find("span", attrs={"data-v-8be6d8ce": True})
    content_text = content_span.text.strip() if content_span else ""

    # Version span
    version_span = row.find("span", class_="table-version", attrs={"data-v-67155f90": True})
    version_text = version_span.text.strip() if version_span else ""

    if content_text or version_text:
        data_list.append([content_text, version_text])
        print(f"{content_text} | {version_text}")

# ---------------- Save to CSV ----------------
with open("lenovo_audio_content_version.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    #writer.writerow(["Content", "Version"])
    writer.writerows(data_list)

print("Data saved to lenovo_audio_content_version.csv")

# Keep browser open
print("Browser is open. Close it manually when done.")
driver.quit()
