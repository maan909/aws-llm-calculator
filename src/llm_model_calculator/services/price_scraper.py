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
OUTPUT_PATH = Path("src/llm_model_calculator/data/latest_prices.json")

def setup_driver():
    options = Options()
    options.headless = True
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    return driver

def scrape_bedrock_dynamic():
    driver = setup_driver()
    logging.info("Loading AWS Bedrock pricing page...")
    driver.get(URL)

    try:
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "table"))
        )
        logging.info("Pricing table detected!")

    except Exception as e:
        logging.error("Timeout waiting for table. DOM structure might have changed.")
        driver.quit()
        return {}

    page_source = driver.page_source
    driver.quit()

    soup = BeautifulSoup(page_source, "html.parser")

    # Optional: Save to debug HTML file
    with open("debug_bedrock_pricing.html", "w", encoding="utf-8") as f:
        f.write(page_source)

    pricing_data = {}

    tables = soup.find_all("table")
    for table in tables:
        rows = table.find_all("tr")

        # Skip if no data rows
        if len(rows) < 2:
            continue

        # Ensure the first row is valid before accessing
        first_row_cols = rows[0].find_all("td")
        if len(first_row_cols) < 2:
            continue  # Skip table if the first row isn't valid

        headers = [td.get_text(strip=True).lower() for td in first_row_cols]
        
        # Checking if it contains the expected headers
        if "price per 1,000 input tokens" not in headers[1]:
            continue

        # Parse actual rows, starting from the second row
        for row in rows[1:]:
            cols = row.find_all("td")
            if len(cols) != 3:
                continue

            model = cols[0].get_text(strip=True)
            input_price = extract_price(cols[1].get_text(strip=True))
            output_price = extract_price(cols[2].get_text(strip=True))

            pricing_data[model] = {
                "input_price": input_price,
                "output_price": output_price,
                "unit": "per 1K tokens",
                "provider": "AI21 Labs",
                "region": "us-east-1"
            }

    if not pricing_data:
        logging.warning("⚠️ Still no data. Check DOM structure again or manual scraping.")
    else:
        logging.info(f"Extracted {len(pricing_data)} models from pricing table.")

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
