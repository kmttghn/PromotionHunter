#  Promotion Hunter
It checks promotions on online grocery stores and reports back in email.
It requires the product identifyer of the product page from the shop. So far it can be found on URL of the item page.
Each store class uses its own scraping method. It might need to consider using headless Selenium in the future.

The OAuth2 authentication is required on the Gmail account used for sending messages.

## Setup
```
pip install -r requirements.txt
```

## 