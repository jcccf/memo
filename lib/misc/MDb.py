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

class MDb:
  def __init__(self, dbfilename):
    if not os.path.exists(dbfilename):
      raise Exception("Database %s Doesn't Exist!" % dbfilename)
    self.filename = dbfilename
    self.conn = sqlite3.connect(dbfilename)
    self.conn.text_factory = str
    self.c = self.conn.cursor()

  def q(self, query):
    self.c.execute(query)
    return self.c.fetchall()
    
  def qt(self, query, tuples):
    self.c.execute(query, tuples)
    return self.c.fetchall()
  
  def close(self):
    self.c.close()

def sql_ins(c, conv_id, movie_name, actor, quote, quote_type, query_type, result, urls, engine='bing'):
  c.execute('INSERT INTO quotes (conv_id, movie, actor, quote, source, quote_type, query_type, result, urls) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)', (conv_id, movie_name, actor, quote, engine, quote_type, query_type, result, urls))