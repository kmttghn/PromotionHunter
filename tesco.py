import requests
import logging
import utils
from bs4 import BeautifulSoup


class Tesco:
    def __init__(self, base_url="https://www.tesco.com/"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update(
            { #The alphabetical order of header items seem to avoid bot detection
                "Accept": "*/*",
                # "Accept-Encoding": "gzip, deflate, br",
                # "Accept-Language": "en-GB,en;q=0.9",
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.6 Safari/605.1.15"
            }
        )
        # self._init_cookie() -- It seems no longer needed

    def _request_wrapper(self, method, path, body):
        url = self.base_url + path
        if method == "POST":
            self.session.headers.update(
                {"Content-Type": "application/json", "Origin": "https://www.tesco.com/"}
            )
            req = requests.Request(method, url, json=body)
        else:
            if "Content-Type" in self.session.headers:
                self.session.headers.pop("Content-Type")
            if "Origin" in self.session.headers:
                self.session.headers.pop("Origin")
            req = requests.Request(method, url)

        prepped = self.session.prepare_request(req)
        # print(prepped.headers)
        # print(prepped.body)

        try:
            response = self.session.send(prepped, timeout=5)
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
        # print(response.request.__dict__)
        # print(response.__dict__)

        return data

    # def _init_cookie(self):
    #     path = f"groceries/en-GB/products/"
    #     response = self._request_wrapper("GET", path, "")
    #     # extract `i`, `j` and `bm-verify`
    #     i = re.search(rb"var i = (\d+)", response)[1]
    #     j = re.search(rb'var j = i [+] Number[(]"(\d+)" [+] "(\d+)"[)]', response)
    #     j = j[1] + j[2]
    #     payload = {
    #         "bm-verify": re.search(rb'"bm-verify"\s*:\s*"([^"]+)', response)[
    #             1
    #         ].decode(),
    #         "pow": int(i) + int(j),
    #     }
    #     # print(f"Payload: {payload}")

    #     path = f"_sec/verify?provider=interstitial"
    #     response = self._request_wrapper("POST", path, payload)
    #     return

    def soup_to_text(self, soup):
        if soup:
            return soup.get_text(" ", strip=True)
        return

    def get_product(self, productId):
        path = f"groceries/en-GB/products/{productId}"

        response = self._request_wrapper("GET", path, "")
        soup = BeautifulSoup(response, "html.parser")

        title = self.soup_to_text(soup.css.select_one("h1[class*='ProductTitle']"))
        price = utils.text_to_float(
            self.soup_to_text(soup.css.select_one("p[class*='PriceText']"))
        )
        unit_price = self.soup_to_text(soup.css.select_one("p[class*='Subtext']"))
        offer_price = utils.text_to_float(
            self.soup_to_text(soup.css.select_one("div[class*='PromotionsContainer'] p[class*='ContentText']"))
        )
        offer_unit_price = self.soup_to_text(soup.css.select_one("div[class*='PromotionsContainer'] p[class*='SubText']"))
        offer_term = self.soup_to_text(soup.css.select_one("div[class*='PromotionsContainer'] p[class*='TermsText']"))
        item = {
            "title": title,
            "price": price,
            "unit_price": unit_price,
            "offer_price": offer_price,
            "offer_unit_price": offer_unit_price,
            "offer_term": offer_term,
            "has_offer": True if offer_price else False,
        }
        # print(item)

        return item


if __name__ == "__main__":
    logging.basicConfig(
        handlers=[logging.StreamHandler()],
        level=logging.INFO,
        format="%(asctime)s %(message)s",
        datefmt="%Y/%m/%d %H:%M:%S",
    )
    tesco = Tesco()
    # print(tesco.getProduct("297105301"))
    print(tesco.get_product("311680104"))
    # tesco.getProduct("313855828")
