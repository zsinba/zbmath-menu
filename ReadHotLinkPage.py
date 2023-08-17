import re

import requests
from bs4 import BeautifulSoup
import pandas as pd


# 去掉大括号及其内的内容
def remove_brackets_content(string):
    pattern = r'\{.*?\}'
    result = re.sub(pattern, '', string)
    return result.strip()


# 去掉尾部的数字
def remove_trailing_digits(string):
    while string and string[-1].isdigit():
        string = string[:-1]
    return string


# 发送HTTP请求并获取网页内容
url = 'https://zbmath.org/classification/'
response = requests.get(url)
html_content = response.text

# 使用BeautifulSoup解析HTML
soup = BeautifulSoup(html_content, 'html.parser')

# 提取父页面的code和half
rows = soup.find_all('article')
parent_data = []
level1_data = []
level2_data = []

# 将父页面和子页面的数据合并到一个列表中
data = []

for row in rows:
    # 取level0级的内容，00，01，02，，，97
    level0_code = row.find('div', class_='code').text.strip()
    level0_half = row.find('div', class_='half').text.strip()
    tmp_l0_code_half = [level0_code, level0_half]
    parent_data.append(tmp_l0_code_half)
    # # 提取子页面的code和text
    code_link = row.find('div', class_='code').find('a')['href']
    response = requests.get('https://zbmath.org' + code_link)
    subpage_content = response.text
    subpage_soup = BeautifulSoup(subpage_content, 'html.parser')
    # 取level1级的标题 00-01，00Axx
    level1 = subpage_soup.find_all('div', class_='item level1')
    # 取level2级的标题 00A05，00A06
    level2 = subpage_soup.find_all('div', class_='item level2')
    for r in level1:
        l1_code = r.find('div', class_='code').text.strip()
        l1_text = r.find('div', class_='text').text.strip()
        tmp_l1_code_text = [l1_code, remove_brackets_content(remove_trailing_digits(l1_text))]
        level1_data.append(tmp_l1_code_text)

        if l1_code.startswith(level0_code.replace('x', '')):
            data.append(tmp_l0_code_half + tmp_l1_code_text)

        if len(level2):
            for l2 in level2:
                l2_code = l2.find('div', class_='code').text.strip()
                l2_text = l2.find('div', class_='text').text.strip()
                tmp_l2_code_text = [l2_code, remove_brackets_content(remove_trailing_digits(l2_text))]
                if l2_code.startswith(l1_code.replace('x', '')):
                    data.append(tmp_l0_code_half + tmp_l1_code_text + tmp_l2_code_text)

# 将提取的数据保存到Excel文件
df = pd.DataFrame(data,
                  columns=['Level0 Code', 'Level0 Half', 'Level1 Code', 'Level1 Text', 'Level2 code', 'Level2 Text'])
df.to_excel('zbmath-level0-level1-level2.xlsx', index=False)
