import pandas as pd

df = pd.read_excel("Anime.xls", engine="xlrd")
df.to_excel("Anime_converted.xlsx", index=False)
