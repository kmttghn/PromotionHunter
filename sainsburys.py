import requests
import logging
# import re
# from bs4 import BeautifulSoup
import collections

class Sainsburys():
    def __init__(self, base_url="https://www.sainsburys.co.uk/"):
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
        self.initCookie()

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
            print(response.request.headers)
            logging.exception(f"HTTP error: {e}")
            raise SystemExit()
        except requests.exceptions.Timeout as e:
            logging.exception(f"The request timed out: {e}")
            raise SystemExit()
        except requests.exceptions.RequestException as e:
            logging.exception(f"Exception: {e}")
            raise SystemExit(e)

        if response.text.startswith("{"):
            # print(response.text)
            try:
                data = response.json()
            except ValueError as e:
                logging.exception(f"Response parse error: No json returned {e}")
                raise SystemExit(e)
            return data
        return

    def initCookie(self):   
        path = f""
        response = self._request_wrapper("GET", path, "")
    
        return
            
    def getProduct(self, productId):
        path = f"groceries-api/gol-services/product/v1/product?filter[product_seo_url]=gb%2Fgroceries%2F{productId}"

        response = self._request_wrapper("GET", path, "")
        # print(response)
        promotion = response.get("products")[0].get("promotions")
        title = response.get("products")[0].get("name")
        if len(promotion) > 0:
            price = promotion[0].get("original_price") 
            unit_price =  str(response.get("products")[0].get("unit_price").get("price")) + "/" + response.get("products")[0].get("unit_price").get("measure")
            offer_price = response.get("products")[0].get("retail_price").get("price") 
            offer_unit_price = str(response.get("products")[0].get("nectar_price").get("unit_price")) + "/" + response.get("products")[0].get("unit_price").get("measure")
            offer_term = "Ends on " + promotion[0].get("end_date") 
        else:
            price = response.get("products")[0].get("retail_price").get("price")
            unit_price =  str(response.get("products")[0].get("unit_price").get("price")) + "/" + response.get("products")[0].get("unit_price").get("measure")
            offer_price = ""
            offer_unit_price = ""
            offer_term = ""
        item = {
            "title": title,
            "price": price,
            "unit_price": unit_price,
            "offer_price": offer_price ,
            "offer_unit_price": offer_unit_price ,
            "offer_term": offer_term,
            "has_offer": True if offer_price else False
        }

        return item
    

    
if __name__ == "__main__":
    logging.basicConfig(
        handlers=[
            logging.StreamHandler()
        ],
        level=logging.INFO, 
        format="%(asctime)s %(message)s", datefmt="%Y/%m/%d %H:%M:%S"
    )
    sains = Sainsburys()
    print(sains.getProduct("aspall-raw-cyder-vinegar--organic-500ml"))
    # print(sains.getProduct("alpro-blueberry-cherry-yogurt-alternative-4x125g"))

