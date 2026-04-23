import requests
from bs4 import BeautifulSoup
#做爬蟲要對網路標籤了解

url = "https://flask-2026b.vercel.app/me"
Data = requests.get(url)
Data.encoding = "utf-8"
#print(Data.text)
sp = BeautifulSoup(Data.text, "html.parser")
result=sp.select("td")
for item in result:
	print(item.text)
	print()