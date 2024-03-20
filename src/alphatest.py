
import requests

apikey = "J3DFCOIAJFPZRN7G"

def call (ticker):
    
    url = f'https://www.alphavantage.co/query?function=OVERVIEW&symbol={ticker}&apikey={apikey}'
    print (f"url used:{url}")
    r = requests.get(url)
    data = r.json()
    print(data)


call(input("Enter ticker: "))


