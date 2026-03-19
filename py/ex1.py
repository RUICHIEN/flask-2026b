def Spilt(x):
    x = x.split(",")
    school = x[0].replace('我是','')
    print(f"學校:{school}")
    print(f"姓名:{x[1]}")

# 這代表只有當你「直接執行 ex1.py」時，下面的程式碼才會跑
# 如果是被 import 到其他檔案，這段就會被跳過
if __name__ == "__main__":
    Name = "我是靜宜大學, AA, BBB"
    Spilt(Name)