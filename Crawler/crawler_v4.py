#%%
from  datetime import date
from bs4  import BeautifulSoup
import json
import requests
import pandas as pd
import re
import time
import numpy as np
# %%
def Crawler(urls):
    def check_status(response):
        try:
            if response.status_code != 200:
                raise Exception(f"代碼 : {response.status_code}")
            return True
        except Exception as e:
            print(e)
            return False

    def get_rating_table(html_doc):
            soup_doc = BeautifulSoup(html_doc.text,"html.parser")
            drama_name = soup_doc.find("title").string[:-11]
            all_table = pd.read_html(html_doc.text)
            get_tables = [table for table in all_table if table.shape[1] >= 10]
            return drama_name,soup_doc,get_tables

    def timeformate(string,check_date):
        string = string[:5]
        ymd = str(check_date.year)+"-"+ string
        try :
            check_d = date.fromisoformat(ymd)
            if (check_d - check_date).days < 0:
                check_d = check_d.replace(year = check_d.year+1)
                ymd = date.isoformat(check_d)
            return ymd

        except ValueError :
            print("before: ",ymd)
            ymd = str(check_date.year+1)+"-"+ string    
            print("after:",ymd)
            return ymd


    def df_preprocess(table,premiere):
        #收視率表格
        rating_table = table.iloc[2:,:3]
        rating_table.columns = table.iloc[1,:3].tolist()
        
        #前處理
        rating_table = rating_table.drop_duplicates(subset= ["集次","播出日期"])
        rating_table = rating_table.dropna()
        rating_table = rating_table[
            ~rating_table["集次"].str.contains("平均") &
            rating_table["播出日期"].str.contains("^\d+") & 
            rating_table["家庭收視率"].str.contains("^\d+")]
        
        check_date = date.fromisoformat(premiere)
        rating_table["播出日期"] = rating_table["播出日期"].apply(timeformate,args=(check_date,))
        rating_table["家庭收視率"] = rating_table["家庭收視率"].map(lambda x:float(x.strip("%"))/100)
        return rating_table


    drama_id = []
    data = {}
    data["drama"] = []
    for url in urls:
        html_doc1 = requests.get(url)
        if check_status(html_doc1) is True:
            soup_doc1 = BeautifulSoup(html_doc1.text,"html.parser")
            # print(soup.prettify())
            main_table = soup_doc1.find(class_ = "table_r table_w").find_all("a",href = re.compile("^/drama-\d+.html"))  
            for i in main_table:
                id_ = i.get("href")[7:-5]
                if id_ in drama_id:continue
                drama_id.append(id_)
                drama_url = f"http://dorama.info/drama-{id_}.html"           
                html_doc2 = requests.get(drama_url)
                print(id_)
                # print(drama_url)

                if check_status(html_doc2) is True:
                    soup_doc2 = BeautifulSoup(html_doc2.text,"html.parser")

                    dramatype = soup_doc2.find("td",class_ = "td2_g",text= re.compile("電視劇$"))
                    search_rating_url =soup_doc2.find("a",href = re.compile("^/drama/pfd_rate"))
                    
                    if dramatype and search_rating_url:
                        
                        print(dramatype.string)
                        rating_url = "http://dorama.info"+search_rating_url["href"]
                        print(rating_url)

                        html_doc3 = requests.get(rating_url)
                        if check_status(html_doc3) is True:
                            drama_name,soup_doc3,rating_table = get_rating_table(html_doc3)
                            print(drama_name)                        
                            try:
                                pages = soup_doc3.find("span",class_ = "disable").find_next_siblings("a")
                                page_url = ["http://dorama.info" + p["href"] for p in pages if p.string]

                                for page in page_url:
                                    html_doc4 = requests.get(page)
                                    _,_, page_table = get_rating_table(html_doc4)
                                    
                                    rating_table.extend(page_table)
                                    time.sleep(1)

                            except AttributeError:
                                print("one page")
                            except Exception as e:
                                print(e)

                            merge_table = {}
                            for table in rating_table:
                                title = table.iloc[0,0]
                                air_info = re.findall("^\w+\s(\w+).*\s(\w+)\s(\d+-\d+-\d+).*(\d{2}:\d{2})",title)
                                area,channle,premiere,air_time = air_info[0]
                                check_year = int(premiere[:4])
                                
                                if area == "關東" and (2018 < check_year < 2021):
                                    rating_table = df_preprocess(table,premiere)
                                    
                                    drama_info = (id_,drama_name,channle,premiere,air_time)

                                    if drama_info in merge_table:
                                        df = merge_table[drama_info]
                                        merge_table[drama_info] = pd.concat([df,rating_table],ignore_index=True)
                                    else:
                                        merge_table[drama_info] = rating_table
                            
                            
                            for k,v in merge_table.items():
                                datum = {}
                                id_,drama_name,channle,premiere,air_time = k
                                df = v
                                display(df.head())
                                datum["id"] = id_
                                datum["name"] = drama_name
                                datum["channle"] = channle
                                datum["premiere"] = premiere
                                datum["air_time"] = air_time
                                datum["df"] = df.to_json()
                                data["drama"].append(datum)
                                print(datum)
                    else:
                        print("out!")

                    print("\n")
                
                time.sleep(1)
        time.sleep(1)
    return data
#%%
if __name__ == "__main__":

    urls = [f"http://dorama.info/drama/d_rate.php?year=2020&season={i}&ord=7" for i in range(1,5)]
    data = Crawler(urls) 
    # %%
    # with open('drama_rating.json', 'w') as outfile:  
    #     json.dump(data, outfile,ensure_ascii=False,indent=2)
# %%
