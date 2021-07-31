# %%
import json
import pandas as pd
# %%
def JsontoDf(data):
    duplicate_id = {}
    df_all = pd.DataFrame()
    for i in data["drama"]:
        id_  = i["id"]
        name = i["name"]
        channle = i["channle"]
        premiere = i["premiere"]
        air_time = i["air_time"]
        df = pd.read_json(i["df"])
        df.columns = ["Episode","Air_date","Family_rating"]
        df["Family_rating"] = df["Family_rating"].round(3)
        if id_ in duplicate_id:
            duplicate_id[id_] += 1
            num = duplicate_id[id_]
            id_ = f"{id_}_{num}"    
        else:
            duplicate_id[id_] = 1
            id_ = f"{id_}_{1}"
        df.insert(0,"Id",id_)  
        df.insert(1,"Name",name)
        df.insert(2,"Channle",channle)
        df.insert(4,"Air_time",air_time)
        df_all = df_all.append(df)
    df_all = df_all.reset_index(drop = True)
    return df_all
# %%
if __name__ == "__main__":
    with open('drama_rating.json') as json_file:  
        data = json.load(json_file)
    df = jsontocsv(data)
    display(df)

#%%