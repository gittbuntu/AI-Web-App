import pandas as pd

path = r"E:\N\business-employment-data-june-2023-quarter\machine-readable-business-employment-data-jun-2023-quarter.csv"

df = pd.read_csv(path)

# print(df.head())

header = ["a","b","c","d","e","f","g","h","i","j","k","l","m","n"]

df.columns = header

save_path = (r"E:\N\ quarter.csv")
df.to_csv(save_path)

print(df.head())
