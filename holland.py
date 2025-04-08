import requests
import logging
import utils
import json
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

        sp = soup.css.select_one("script#__LAYOUT__")
        if sp:
            product_data = json.loads(sp.text)["resolveParamValues"]["7251734e-0355-43f8-aa7f-79e58b318ab4"]["data"]

            title = product_data.get("title") 
            original_price = utils.text_to_float(product_data["price"].get("preSalePrice"))
            if original_price:
                price = original_price
                unit_price = None
                offer_price = utils.text_to_float(product_data["price"].get("price"))
                offer_unit_price = product_data["price"].get("pricePerUom")
                offer_term = product_data["promos"][0].get("text")
            else:
                price = utils.text_to_float(product_data["price"].get("price"))
                unit_price = product_data["price"].get("pricePerUom")
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
    print(holland.get_product("applied-nutrition-marine-collagen-strawberry-raspberry-300g-6100003873"))
    

