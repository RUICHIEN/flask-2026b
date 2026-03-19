def square(y):
  print(f"{y} 的平方為 {y*y}")


x=int(input('請輸入:'))
#x+=10
#print('輸入:',x)
if (x<=0):
	print(f'您輸入的數字{x}小魚等魚0')
else:
	print(f'您輸入的數字{x}大於0')
	for i in range(1,x+1):
		#print(i,end="; ")
		square(i)
