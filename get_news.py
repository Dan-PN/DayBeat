
# %%
from pygooglenews import GoogleNews
import pandas as pd


gn = GoogleNews(lang='en')
top_news = gn.top_news()

data_news = pd.DataFrame(columns=["title"])

title_list = []
for i in top_news['entries']:
    print(i['title'])
    title_list.append(i['title'])

data_news = pd.DataFrame(data=title_list, columns=["title"])
d = data_news.title.str.rsplit("-", n=1, expand=True)
data_news.title = d[0]


# %%


# %%

# %%

# %%