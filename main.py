import logging
from datetime import datetime
# from tesco import Tesco
from tescoSel import Tesco #It does not work on a-shell environment as ChromeWebDriver is not accesible via the shell
from sainsburys import Sainsburys
from holland import Holland
from waitrose import Waitrose
from morrisons import Morrisons
from gmail import Gmail
import config

def main():
    products = config.PRODUCTS

    def sendReport(products):
        message = {"To":config.MESSAGE_TO, 
            "From": config.MESSAGE_FROM,
            "Subject":f"Promotion Hunter Report {datetime.today().strftime('%Y-%m-%d')}",
            "Body": ""}
        body = []
        for product in products:
            offer_item = [item for item in product.get("items") if item["has_offer"] == True]
            item_offer_message = "It has an offer!" if len(offer_item) > 0 else "No offer found."
            body.append(f"----------")
            body.append(f"[{product['title']}] {item_offer_message}")
            for item in product.get("items"):
                if item.get("has_offer"):
                    body.append(f"* {item.get('store')} - {item.get('title')} \n   Price: {item.get('offer_price')} ({item.get('offer_unit_price')}) \n   Term: {item.get('offer_term')}")
                else:
                    body.append(f"  {item.get('store')} - {item.get('title')} \n   Price: {item.get('price')} ({item.get('unit_price')})")

        message["Body"] = "\n".join(body)
        gmail = Gmail()
        gmail.send_message(message)


    sains = Sainsburys()
    tesco = Tesco()
    holland = Holland()
    waitrose = Waitrose()
    morrisons = Morrisons()
    for idx, product in enumerate(products):
        print("--Looking for:" + product.get("title"))
        for idx2,item in enumerate(product.get("items")):
            match item.get("store"):
                case "Sainsburys":
                    itemDetail = sains.getProduct(item.get("productId"))
                case "Tesco":
                    itemDetail = tesco.getProduct(item.get("productId"))
                case "Holland":
                    itemDetail = holland.getProduct(item.get("productId"))
                case "Waitrose":
                    itemDetail = waitrose.getProduct(item.get("productId"))
                case "Morrisons":
                    itemDetail = morrisons.getProduct(item.get("productId"))
                case _:
                    print ("Something's wrong")
            # print(itemDetail)
            product["items"][idx2] = item | itemDetail
        # print(product["items"])
        products[idx]["items"] = sorted(product.get("items"), key=lambda d:  d.get("offer_price") if d.get("offer_price") else d.get("price") if d.get("price") else 100 )


    # print(products)
    sendReport(products)

 
if __name__ == "__main__":
    logging.basicConfig(
        handlers=[
            logging.FileHandler(r"./promotion.log", mode="a"),
            logging.StreamHandler(),
        ],
        level=logging.INFO,
        format="%(asctime)s %(message)s",
        datefmt="%Y/%m/%d %H:%M:%S",
    )
    logging.info("Started")
    main()
    logging.info("Finished")
