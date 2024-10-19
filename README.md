#  Promotion Hunter
It checks promotions on online grocery stores and reports back in an email.
It requires the product identifier of the product page from the shop. So far it can be found in the URL of the item page.
Each store class uses its own scraping method. 
ChatGPT does better ToT, but their API doesn't provide scraping functions.

The OAuth2 authentication is required on the Gmail account used for sending messages.
## Setup
```
pip install -r requirements.txt
```

## 