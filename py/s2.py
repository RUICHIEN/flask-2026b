import requests
from bs4 import BeautifulSoup
#做爬蟲要對網路標籤了解

url = "https://flask-2026b.vercel.app/me"
Data = requests.get(url)
Data.encoding = "utf-8"
#print(Data.text)
sp = BeautifulSoup(Data.text, "html.parser")
result=sp.find("h1")
#s2版本在這邊做更動
#select-->所有提及都會抓到 / find -->只會標籤第一筆資料
for item in result:
	print(item.text)
	print()