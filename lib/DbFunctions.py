import sqlite3, os.path

# Create the appropriate SQLite tables to store data
def db_prepare(dbfilename):
  if not os.path.exists(dbfilename):
    conn = sqlite3.connect(dbfilename)
    c = conn.cursor()
    c.execute('''CREATE TABLE quotes (movie text, actor text, quote text, source text, quote_type text, query_type text, result int, urls text)''')
    conn.commit()
    c.close()
    print 'Prepared Database Schema for %s' % dbfilename
  else:
    print 'Database Already Exists for %s' % dbfilename