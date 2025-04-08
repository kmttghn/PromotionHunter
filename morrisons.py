import requests
import logging
import utils
import collections
from bs4 import BeautifulSoup

class Morrisons():
    # https://groceries.morrisons.com/products/aspall-raw-organic-apple-cyder-vinegar-431504011
    def __init__(self, base_url="https://groceries.morrisons.com/"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Encoding": "gzip, deflate, br",
                "Accept-Language": "en-GB,en;q=0.9",
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4.1 Safari/605.1.15"
            })
        self.session.headers = collections.OrderedDict(
            ((key, value) for key, value in sorted(self.session.headers.items()))
        )
    
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
        path = f"products/{productId}"

        response = self._request_wrapper("GET", path, "")
        soup = BeautifulSoup(response, "html.parser")
        title = self.soup_to_text(soup.css.select_one("header[class='bop-title'] h1"))
        original_price = utils.text_to_float(self.soup_to_text(soup.css.select_one("span[class*='bop-price__old']")))
        if original_price:
            price = original_price
            unit_price = None
            offer_price = utils.text_to_float(self.soup_to_text(soup.css.select_one("h2[class~='bop-price__current']")))
            offer_unit_price = self.soup_to_text(soup.css.select_one("span[class='bop-price__per']"))
            offer_term = None
        else:
            price = utils.text_to_float(self.soup_to_text(soup.css.select_one("h2[class~='bop-price__current']")))
            unit_price = self.soup_to_text(soup.css.select_one("span[class='bop-price__per']"))
            offer_price = None
            offer_unit_price = None
            offer_term = None
        item = {
            "title": title,
            "price": price ,
            "unit_price": unit_price ,
            "offer_price": offer_price ,
            "offer_unit_price": offer_unit_price ,
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
    morrisons = Morrisons()
    print(morrisons.get_product("beavertown-neck-oil-session-ipa-621747011"))


