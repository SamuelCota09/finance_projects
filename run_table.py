import sqlite3
import pandas as pd

connection = sqlite3.connect('DataPatterns.db')
query = "SELECT * FROM data_p"
df = pd.read_sql(query, connection)
connection.close()

print(df)
