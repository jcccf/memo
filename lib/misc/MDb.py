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
    
def db_prepare_movie(dbfilename):
  if not os.path.exists(dbfilename):
    conn = sqlite3.connect(dbfilename)
    c = conn.cursor()
    c.execute('''CREATE TABLE quotes (id integer primary key autoincrement, conv_id int, movie text, actor text, quote text, source text, quote_type text, query_type text, result int, urls text)''')
    conn.commit()
    c.close()
    print 'Prepared Database Schema for %s' % dbfilename
  else:
    print 'Database Already Exists for %s' % dbfilename
    
def sql_ins(c, conv_id, movie_name, actor, quote, quote_type, query_type, result, urls):
  c.execute('INSERT INTO quotes (conv_id, movie, actor, quote, source, quote_type, query_type, result, urls) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)', (conv_id, movie_name, actor, quote, 'bing', quote_type, query_type, result, urls))