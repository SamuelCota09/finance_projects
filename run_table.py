import sqlite3
import pandas as pd

connection = sqlite3.connect('DataPatterns.db')
query = "SELECT * FROM data_p"
df = pd.read_sql(query, connection)
connection.close()

industry = [
	'Tech', 'Tech', 'Tech', 'Tech', 'Tech',
	'Finance', 'Finance', 'Finance', 'Finance', 'Finance',
	'Energy', 'Energy', 'Energy', 'Energy', 'Energy', 
	'Health',  'Health', 'Health', 'Health', 'Health', 
	'Consume', 'Consume', 'Consume', 'Consume', 'Consume', 
	'Industry', 'Industry', 'Industry', 'Industry', 'Industry',
	'China / Global', 'China / Global', 'China / Global', 'China / Global', 'China / Global', 
	'ETFs', 'ETFs', 'ETFs', 'ETFs', 'ETFs'
	]

df['Industry'] = industry

# --- SMA 15,20 ---

# Initialize pivot as a DataFrame

pivot = pd.DataFrame()

if 'Short_SMA' in df.columns and 'Long_SMA' in df.columns:
	pivot['Short_SMA'] = df['Short_SMA']
	pivot['Long_SMA'] = df['Long_SMA']
	
	pivot = pivot.drop_duplicates()

	pivot['Frequency'] = df.groupby(['Short_SMA', 'Long_SMA'])['Short_SMA'].transform('count')
else:
	print("Required columns are missing in the DataFrame.")

print(f"\n --- FREQUENCY TABLE --- \n \n {pivot} \n")

# Filter rows where Short_SMA is 15 and Long_SMA is 20

filtered_df = df[(df['Short_SMA'] == 15) & (df['Long_SMA'] == 20)]

# Group the filtered DataFrame by Industry

industry_table = filtered_df.groupby('Industry')['Ticker'].apply(list).reset_index()

# Rename columns for clarity

industry_table.columns = ['Industry', 'Tickers']

print(f"\n--- SMA 15,20 Tickers by Industry --- \n \n {industry_table}\n")

print("In the time period from 2023-04-25 to 2025-08-12, most Health and ETFs Tickers perfomed best on an SMA short of 15 and an SMA long of 20")

# --- SMA 10,20 ---

# Filter rows where Short_SMA is 10 and Long_SMA is 20

filtered_df = df[(df['Short_SMA'] == 10) & (df['Long_SMA'] == 20)]

# Group the filtered DataFrame by Industry

industry_table = filtered_df.groupby('Industry')['Ticker'].apply(list).reset_index()

# Rename columns for clarity

industry_table.columns = ['Industry', 'Tickers']

print(f"\n--- SMA 10,20 Tickers by Industry --- \n \n {industry_table}\n")

print("In the time period from 2023-04-25 to 2025-08-12, most Tech Tickers perfomed best on an SMA short of 10 and an SMA long of 20")

# --- SMA 5,20 ---

# Filter rows where Short_SMA is 5 and Long_SMA is 20

filtered_df = df[(df['Short_SMA'] == 5) & (df['Long_SMA'] == 20)]

# Group the filtered DataFrame by Industry

industry_table = filtered_df.groupby('Industry')['Ticker'].apply(list).reset_index()

# Rename columns for clarity

industry_table.columns = ['Industry', 'Tickers']

print(f"\n--- SMA 5,20 Tickers by Industry --- \n \n {industry_table}\n")

print("In the time period from 2023-04-25 to 2025-08-12, most Energy and Finance Tickers perfomed best on an SMA short of 5 and an SMA long of 20")
