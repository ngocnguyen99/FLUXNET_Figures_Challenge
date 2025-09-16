from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import urllib.parse, time, re
import csv

def make_driver():
    opts = webdriver.ChromeOptions()
    # Comment/uncomment the next line if you want headless mode
    # opts.add_argument("--headless=new")
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=opts)

def scholar_count(query, start_year, end_year, driver, timeout=12):
    q = urllib.parse.quote_plus(query)
    url = f'https://scholar.google.com/scholar?as_ylo={start_year}&as_yhi={end_year}&q={q}'
    print(f"Opening: {url}")  # <-- DEBUG so you see the correct years
    driver.get(url)
    try:
        wait = WebDriverWait(driver, timeout)
        el = wait.until(EC.presence_of_element_located((By.ID, "gs_ab_md")))
        stats = el.text.strip()
        print("Raw stats:", stats)
        m = re.search(r'([\d,]+)\s+results', stats)
        if m:
            return int(m.group(1).replace(',', ''))
        return 0
    except Exception as e:
        print("Error getting stats:", e)
        return 0

def main():
    query = '"eddy covariance" "earth system models"'
    driver = make_driver()
    results = []
    try:
        # Year-to-year windows: 2024-2025, 2023-2024, …, 1995-1996
        for year in range(2024, 1994, -1):
            start = year
            end = year + 1
            count = scholar_count(query, start, end, driver)
            results.append({'Year_Range': f'{start}-{end}', 'Count': count})
            print(f"{start}-{end}: {count}\n")
            time.sleep(4)  # throttle requests
    finally:
        driver.quit()

    csv_file = 'scholar_counts.csv'
    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['Year_Range', 'Count'])
        writer.writeheader()
        for r in results:
            writer.writerow(r)

    print(f"Done! Results saved to {csv_file}")


if __name__ == "__main__":
    main()