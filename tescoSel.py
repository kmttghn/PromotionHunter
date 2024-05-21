import requests
import logging
import re
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By



class Tesco:
    def __init__(self, base_url="https://www.tesco.com/"):
        self.base_url = base_url
        self.options = Options()
        # self.options.add_argument('--headless=new') #headless is not able to overcome the token initialisation
        # self.options.add_argument('--disable-blink-features=AutomationControlled')
        self.driver = webdriver.Chrome(options=self.options)


    def textToFloat(self, text):
        if text:
            extract = re.search(r"(\d+\.\d+)", text)
            return float(extract.group()) if extract else None
        return

    def soupToText(self, soup):
        if soup:
            return soup.get_text(" ", strip=True)
        return

    def getProduct(self, productId):
        path = f"groceries/en-GB/products/{productId}"

        url = self.base_url + path
        self.driver.get(url)
        try:
        # Wait for the element with the ID of wrapper
            WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "asparagus-root"))
            )
            print("Element is present in the DOM now")
        except TimeoutException:
            print("Element did not show up")

        htmlsource = self.driver.page_source  
        # print(self.driver.title)

        soup = BeautifulSoup(htmlsource, "html.parser")

        title = self.soupToText(soup.css.select_one("h1[class*='ProductTitle']"))
        price = self.textToFloat(
            self.soupToText(soup.css.select_one("p[class*='PriceText']"))
        )
        unit_price = self.soupToText(soup.css.select_one("p[class*='Subtext']"))
        offer_price = self.textToFloat(
            self.soupToText(soup.css.select_one("span[class*='OfferText']"))
        )
        offer_term = self.soupToText(soup.css.select_one("p[class*='TermsMessage']"))
        item = {
            "title": title,
            "price": price,
            "unit_price": unit_price,
            "offer_price": offer_price,
            "offer_unit_price": "",
            "offer_term": offer_term,
            "has_offer": True if offer_price else False,
        }
        print(item)

        return item


if __name__ == "__main__":
    logging.basicConfig(
        handlers=[logging.StreamHandler()],
        level=logging.INFO,
        format="%(asctime)s %(message)s",
        datefmt="%Y/%m/%d %H:%M:%S",
    )
    tesco = Tesco()
    print(tesco.getProduct("297105301"))
    # tesco.getProduct("313858318")
    # tesco.getProduct("313855828")
