# %%
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# %%
def dropdown_menu_plot(df,title):
    fig = go.Figure()
    
    for column in df.columns.tolist():
        fig.add_trace(
            go.Scatter(
                x = df.index[df[column].notnull()],
                y = df[column][df[column].notnull()],
                name = column[1])
                )
    button_all = dict(
                    label = 'All',
                    method = 'update',
                    args = [{'visible':df.columns.isin(df.columns),'title':'All','showlegend':True}]
                        )
    
    def create_layout_button(column):
        return dict(label = column[1],
                    method = 'update',
                    args = [{'visible': df.columns.isin([column]),'title': column[1],'showlegend': True}])

    
    fig.update_layout(
        updatemenus=[go.layout.Updatemenu(
        active = 0,
        buttons =([button_all]*True)+
            list(df.columns.map(lambda column: create_layout_button(column)))
        )])

    fig.update_layout(xaxis=dict(type='category'),yaxis=dict(title='收視率'),title_text=title,height=600,width = 800)

    fig.show()
# %%
if __name__ == "__main__":
    drama_JP2020 = pd.read_csv("drama_rating_df.csv")
    drama_pivot = pd.pivot_table(drama_JP2020,values = "Family_rating", index="Episode",columns= ["Id","Name"])
    dropdown_menu_plot(drama_pivot,"2020 日本偶像劇收視率")
# %%
