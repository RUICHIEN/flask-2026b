import requests,json
url = "https://datacenter.taichung.gov.tw/swagger/OpenData/a1b899c0-511f-4e3d-b22b-814982a97e41"
headers = {'User-Agent':'Mozilla/5.0'}

Data = requests.get(url,headers=headers,timeout=10)
# print(Data.text)

JsonData = json.loads(Data.text)
Result = ""
for item in JsonData:
	# Result += item["路口名稱"] + "：發生" + item["總件數"] + "件，主因是" + item["主要肇因"] + "\n\n"
	# print(Result)
	print(item['路口名稱'] +',原因:',item['主要肇因'])
	print()
