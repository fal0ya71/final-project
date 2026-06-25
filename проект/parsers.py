import time
import urllib.parse
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

def create_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=options)

def parse_symptoms(symptoms_text):
    encoded = urllib.parse.quote(symptoms_text)
    url = f"https://health.mail.ru/search/?q={encoded}"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code != 200:
            return f"Сайт временно недоступен (код {resp.status_code})."
        soup = BeautifulSoup(resp.text, "html.parser")
        items = soup.select("a[href*='/disease/'], a[href*='/illness/'], .search-result__title a")
        diseases = []
        for item in items[:10]:
            text = item.get_text(strip=True)
            if text and len(text) > 3:
                diseases.append(text)
        unique = list(dict.fromkeys(diseases))[:3]
        if unique:
            return "Возможные заболевания:\n• " + "\n• ".join(unique)
        return "По вашему запросу ничего не найдено."
    except Exception as e:
        return f"Ошибка при поиске симптомов: {e}"

def parse_drugs(disease_name):
    encoded = urllib.parse.quote(disease_name)
    search_url = f"https://www.rlsnet.ru/search/?q={encoded}&type=nosology"
    driver = None
    try:
        driver = create_driver()
        driver.get("https://www.rlsnet.ru/")
        time.sleep(2)
        try:
            search_input = driver.find_element(By.CSS_SELECTOR, "input[name='q'], input[type='text'], input.search")
            search_input.clear()
            search_input.send_keys(disease_name)
            search_input.send_keys(Keys.RETURN)
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".search-result__item a, .search-result a, a[href*='/nosology/']"))
            )
        except:
            driver.get(search_url)
            time.sleep(3)

        items = driver.find_elements(By.CSS_SELECTOR, ".search-result__item a, .search-result a, a[href*='/nosology/']")
        drugs = []
        for el in items[:8]:
            text = el.text.strip()
            if text and len(text) > 2 and "google" not in text.lower() and "поиск" not in text.lower() and "цены" not in text.lower():
                drugs.append(text)
        unique = list(dict.fromkeys(drugs))[:5]
        if unique:
            return "Рекомендованные препараты:\n• " + "\n• ".join(unique)
        return f"Лекарства не найдены. Ссылка: {search_url}"
    except Exception as e:
        return f"Ошибка: {e}\nСсылка: {search_url}"
    finally:
        if driver:
            driver.quit()