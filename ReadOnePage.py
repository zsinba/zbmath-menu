import requests
import pandas as pd
from bs4 import BeautifulSoup
import openpyxl

url = 'https://zbmath.org/classification/'

# 发起HTTP请求并获取网页内容
response = requests.get(url)
html = response.content

soup = BeautifulSoup(html, 'html.parser')

code_column = []
halt_column = []

articles = soup.find_all('article')

for article in articles:
    code_div = article.find('div', class_='code')
    code = code_div.text.strip()
    code_column.append(code)

    halt_div = article.find('div', class_='half')
    halt = halt_div.text.strip()
    halt_column.append(halt)

data = {'Code': code_column, 'Halt': halt_column}
df = pd.DataFrame(data)

df.to_excel('zbmath-level0.xlsx', index=False)
