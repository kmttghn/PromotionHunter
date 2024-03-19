import requests
import logging
import re
from bs4 import BeautifulSoup

class Waitrose():
    # https://www.waitrose.com/ecom/products/aspall-raw-organic-cyder-vinegar/626811-535366-535367
    def __init__(self, base_url="https://www.waitrose.com/"):
        self.base_url = base_url
        self.session = requests.Session()
        # print(requests.utils.default_headers())
        self.session.headers.update({"User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"})

    
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
        
        # print(response.request.headers)
        if response.content:
            data = response.content
        # print(data)     
        return data
    
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
        path = f"ecom/products/{productId}"

        response = self._request_wrapper("GET", path, "")
        soup = BeautifulSoup(response, "html.parser")
        title = self.soupToText(soup.css.select_one("h1[id='productName']"))
        original_price = self.textToFloat(self.soupToText(soup.css.select_one("span[class*='offerDescription'] em")))
        if original_price:
            price = original_price
            unit_price = None
            offer_price = self.textToFloat(self.soupToText(soup.css.select_one("span[data-test='product-pod-price']")))
            offer_unit_price = self.soupToText(soup.css.select_one("span[class*='pricePerUnit']"))
            offer_term = None
        else:
            price = self.textToFloat(self.soupToText(soup.css.select_one("span[data-test='product-pod-price']")))
            unit_price = self.soupToText(soup.css.select_one("span[class*='pricePerUnit']"))
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
    waitrose = Waitrose()
    
    print(waitrose.getProduct("aspall-raw-organic-cyder-vinegar/626811-535366-535367"))
    # print(waitrose.getProduct("aspall-apple-cyder-vinegar-with-honey/563078-680123-680124"))


