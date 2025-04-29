#!/usr/bin/env python3
import time, requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from requests.exceptions import ReadTimeout, RequestException

BASE_URL = "https://www.tesco.com/groceries/en-GB/products/{id}"
START_ID, END_ID = 250_000_000, 300_000_000

def make_session():
    s = requests.Session()
    s.headers.update({ "User-Agent": "tesco-scraper/1.0" })
    retries = Retry(
        total=3, backoff_factor=1,
        status_forcelist=[429,500,502,503,504],
        allowed_methods=["GET"]
    )
    adapter = HTTPAdapter(max_retries=retries)
    s.mount("https://", adapter)
    return s

def fetch_product(pid, session):
    url = BASE_URL.format(id=pid)
    try:
        resp = session.get(url, timeout=(3,15))
        resp.raise_for_status()
    except ReadTimeout:
        print(f"[{pid}] ⚠️ timeout")
        return None, None
    except RequestException as e:
        print(f"[{pid}] ⚠️ request error: {e}")
        return None, None

    soup = BeautifulSoup(resp.text, "html.parser")
    # … parse name & price as before …
    return name, price

def main():
    session = make_session()
    with open("tesco_products.txt", "w", encoding="utf-8") as fout:
        fout.write("Name – Price\n================\n")
        for pid in range(START_ID, END_ID+1):
            name, price = fetch_product(pid, session)
            if name and price:
                fout.write(f"{name} – {price}\n")
                print(f"[{pid}] {name} – {price}")
            time.sleep(0.2)    # polite throttle

if __name__ == "__main__":
    main()

