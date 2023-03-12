import re

# 读取本地的html文件
with open("白雲.htm", encoding="utf-8") as f:
    html = f.read()

# 第一种链接格式的正则表达式
pattern1 = r'<td><a href="(.*?)">(.*?)</a>(.*?)</td>'

# 第二种链接格式的正则表达式
pattern2 = r'<a href="(.*?)">(.*?)</a>(.*?)<br>'

# 匹配第一种链接格式并输出结果
for match in re.findall(pattern1, html):
    print(f"{match[1]}，{match[2]}，{match[0]}")

# 匹配第二种链接格式并输出结果
for match in re.findall(pattern2, html):
    print(f"{match[1].strip()}，{match[2].strip()}，{match[0]}")
