import requests
import logging
import re
from bs4 import BeautifulSoup

class Tesco():
    def __init__(self, base_url="https://www.tesco.com/"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update(
            {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36",
             "Referer":"https://www.tesco.com/"})
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
                
        return data
    
    def initCookie(self):   
        path = f"groceries/en-GB/products/"
        response = self._request_wrapper("GET", path, "")
        # print(response)
        # extract `i`, `j` and `bm-verify`
        i = re.search(rb'var i = (\d+)', response)[1]
        j = re.search(rb'var j = i [+] Number[(]"(\d+)" [+] "(\d+)"[)]', response)
        j = j[1] + j[2]
        payload = {
        'bm-verify': re.search(rb'"bm-verify"\s*:\s*"([^"]+)', response)[1].decode(),
        'pow': int(i) + int(j)
        }

        path = f"/_sec/verify?provider=interstitial"
        response = self._request_wrapper("POST", path, payload)
        # print(response)
        return

           
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

        response = self._request_wrapper("GET", path, "")
        soup = BeautifulSoup(response, "html.parser")

        title = self.soupToText(soup.css.select_one("h1[class*='ProductTitle']"))
        price = self.textToFloat(self.soupToText(soup.css.select_one("p[class*='PriceText']")))
        unit_price = self.soupToText(soup.css.select_one("p[class*='Subtext']"))
        offer_price = self.textToFloat(self.soupToText(soup.css.select_one("span[class*='OfferText']")))
        offer_term = self.soupToText(soup.css.select_one("p[class*='TermsMessage']"))
        item = {
            "title": title,
            "price": price,
            "unit_price": unit_price,
            "offer_price": offer_price,
            "offer_unit_price": "" ,
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
    tesco = Tesco()
    print(tesco.getProduct("297105301"))
    # tesco.getProduct("313858318")
    # tesco.getProduct("313855828")

