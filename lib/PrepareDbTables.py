# PrepareDbTables
# Create the appropriate SQLite tables to store data

import sqlite3

conn = sqlite3.connect('../data/db.sqlite')
c = conn.cursor()

c.execute('''CREATE TABLE quotes (movie text, actor text, quote text, source text, query_type text, result int, urls text)''')

conn.commit()

c.close()