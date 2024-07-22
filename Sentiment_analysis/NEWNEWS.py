from urllib.request import urlopen, Request
from bs4 import BeautifulSoup
from datetime import date 

raw_url = "https://finviz.com/quote.ashx?t="
stock = "MSFT"

today = date.today()

news_data = {}
url = raw_url +stock
req = Request(url = url, headers={"user-agent": "my-app"})
response = urlopen(req)

html = BeautifulSoup(response, "html")
news_table = html.find(id = "news-table")
news_data[stock] = news_table

stock_news = news_data[stock]
stock_rows = stock_news.findAll("tr")

print(html)
print(stock_rows)

for index, row in enumerate(stock_rows):
    try:
        title = row.a.text
        timestamp = row.td.text
    except AttributeError:#filters out ads
        print("error ig\n\n\n\n\n")
        continue
    print(timestamp)
    print(title)