# src/llm_model_calculator/services/dynamic_scraper.py

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import json
from pathlib import Path
import time
import logging

logging.basicConfig(level=logging.INFO)

URL = "https://aws.amazon.com/bedrock/pricing/"
OUTPUT_PATH = Path("C:\\Users\\MaanPatel\\OneDrive - CloudThat\\projects\\llm_cal_project\\src\\llm_model_calculator\\data\\latest_prices.json")

def setup_driver():
    options = Options()
    options.headless = True
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    return driver

def scrape_bedrock_dynamic():
    driver = setup_driver()
    logging.info("🔄 Loading AWS Bedrock pricing page...")
    driver.get(URL)

    try:
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "table"))
        )
        logging.info("✅ Pricing table detected!")

    except Exception as e:
        logging.error("⏱️ Timeout waiting for table. DOM structure might have changed.")
        driver.quit()
        return {}

    page_source = driver.page_source
    driver.quit()

    soup = BeautifulSoup(page_source, "html.parser")
    pricing_data = {}

    tables = soup.find_all("table")
    for table in tables:
        rows = table.find_all("tr")

        if len(rows) < 2:
            continue

        headers = [td.get_text(strip=True).lower() for td in rows[0].find_all("td")]
    
        if not headers:
            continue  # 👈 Safely skip this table if no headers were found

        if "anthropic models" in headers[0]:
            for row in rows[1:]:
                cols = row.find_all("td")
                if len(cols) != 7:
                    continue
                model = cols[0].get_text(strip=True).replace("\n", " ").replace("  ", " ")
                pricing_data[model] = {
                "input_price": extract_price(cols[1].get_text(strip=True)),
                "output_price": extract_price(cols[2].get_text(strip=True)),
                "batch_input_price": extract_price(cols[3].get_text(strip=True)),
                "batch_output_price": extract_price(cols[4].get_text(strip=True)),
                "cache_write_price": extract_price(cols[5].get_text(strip=True)),
                "cache_read_price": extract_price(cols[6].get_text(strip=True)),
                "unit": "per 1K tokens",
                "provider": "Anthropic",
                "region": "us-east-1 / us-west-2"
             }

        elif len(headers) >= 2 and "price per 1,000 input tokens" in headers[1]:
            for row in rows[1:]:
                cols = row.find_all("td")
                if len(cols) != 3:
                    continue
                model = cols[0].get_text(strip=True)
                pricing_data[model] = {
                "input_price": extract_price(cols[1].get_text(strip=True)),
                "output_price": extract_price(cols[2].get_text(strip=True)),
                "unit": "per 1K tokens",
                "provider": "AI21 Labs",
                "region": "us-east-1"
            }

    if not pricing_data:
        logging.warning("⚠️ Still no data. Check DOM structure again or manual scraping.")
    else:
        logging.info(f"✅ Extracted {len(pricing_data)} models from pricing table.")

    return pricing_data


def extract_price(price_str):
    try:
        return float(price_str.replace("$", "").replace(",", "").split()[0])
    except:
        return None

def normalize_model_name(name):
    return name.lower().replace(" ", "-").replace("(", "").replace(")", "")

def save_to_json(data, path=OUTPUT_PATH):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=4)
    logging.info(f"✅ Pricing data saved to: {path}")

def run_scraper():
    prices = scrape_bedrock_dynamic()
    if prices:
        save_to_json(prices)
    else:
        logging.warning("Still no data. Check DOM structure again or manual scraping.")

if __name__ == "__main__":
    run_scraper()
