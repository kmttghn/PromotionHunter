import requests
import logging
import utils
from bs4 import BeautifulSoup

class Holland():
    # https://www.hollandandbarrett.com/shop/product/aspall-raw-organic-unfiltered-cyder-vinegar-60011461
    def __init__(self, base_url="https://www.hollandandbarrett.com/"):
        self.base_url = base_url
        self.session = requests.Session()
    
    def _request_wrapper(self, method, path, body):
        url = self.base_url + path
        if method == "POST":
            req = requests.Request(method, url, json=body)
        else:
            req = requests.Request(method, url)

        prepped = self.session.prepare_request(req)

        try:
            response = self.session.send(prepped, timeout=3)
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            logging.exception(f"HTTP error: {e}")
            raise SystemExit()
        except requests.exceptions.Timeout as e:
            logging.exception(f"The request timed out: {e}")
            raise SystemExit()
        except requests.exceptions.RequestException as e:
            logging.exception(f"Exception: {e}")
            raise SystemExit(e)
        
        if response.content:
            data = response.content
        # print(data)     
        return data
    
    def soup_to_text(self, soup):
        if soup:
            return soup.get_text(" ", strip=True)
        return
    
    def get_product(self, productId):
        path = f"shop/product/{productId}"

        response = self._request_wrapper("GET", path, "")
        soup = BeautifulSoup(response, "html.parser")
        title = self.soup_to_text(soup.css.select_one("h1[class*='ProductHeaderUI-module_title']"))
        original_price = utils.text_to_float(self.soup_to_text(soup.css.select_one("p[class*='wasPrice']")))
        if original_price:
            price = original_price
            unit_price = None
            offer_price = utils.text_to_float(self.soup_to_text(soup.css.select_one("p[class*='nowPrice']")))
            offer_unit_price = self.soup_to_text(soup.css.select_one("p[class*='pricePerUom']"))
            offer_term = self.soup_to_text(soup.css.select_one("a[class*='PromoFlag-module_flag']"))
        else:
            price = utils.text_to_float(self.soup_to_text(soup.css.select_one("p[class*='nowPrice']")))
            unit_price = self.soup_to_text(soup.css.select_one("p[class*='pricePerUom']"))
            offer_price = None
            offer_unit_price = None
            offer_term = None
        item = {
            "title": title,
            "price": price,
            "unit_price": unit_price,
            "offer_price": offer_price,
            "offer_unit_price": offer_unit_price,
            "offer_term": offer_term,
            "has_offer": True if offer_price else False
        }
        # print(item)

        return item
    

    
if __name__ == "__main__":
    logging.basicConfig(
        handlers=[
            logging.StreamHandler()
        ],
        level=logging.INFO, 
        format="%(asctime)s %(message)s", datefmt="%Y/%m/%d %H:%M:%S"
    )
    holland = Holland()
    print(holland.get_product("aspall-raw-organic-unfiltered-cyder-vinegar-60011461"))

