# %%
import json
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from pprint import pprint

# %%
#2020日本偶像劇收視率網址
urls = [f"http://dorama.info/drama/d_rate.php?year=2020&season={i}&ord=7" for i in range(1,5)]
urls
# %%
#爬取 2020每部偶像劇的收視率
from crawler_v4 import Crawler #載入自定義函數
data = Crawler(urls) #json格式
data
# %%
#存為json檔
with open('drama_rating.json', 'w') as outfile:  
    json.dump(data, outfile,ensure_ascii=False,indent=2)
# %%
#讀取json檔
with open('drama_rating.json') as json_file:  
        data = json.load(json_file)
pprint(data)
# %%
#json轉為dataframe
from drama_rating_to_csv import JsontoDf #載入自定義函數
df = JsontoDf(data)
df
# %%
#存為csv檔
df.to_csv("drama_rating_df.csv",index = False,header = True)
# %%
#讀取csv檔
drama_JP2020 = pd.read_csv("drama_rating_df.csv")
drama_JP2020
# %%
#轉成樞紐分析表
drama_pivot = pd.pivot_table(drama_JP2020,values = "Family_rating", index="Episode",columns= ["Id","Name"])
drama_pivot

# %%
#2020 日本偶像劇收視率視覺化
from data_visuliation import dropdown_menu_plot
dropdown_menu_plot(drama_pivot,"2020 日本偶像劇收視率")

# %%