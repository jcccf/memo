import sqlite3, os.path
import MQuote

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

class MDb(object):
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

class MDbQuotes(MDb):
  
  # Helper Match Functions
  
  def match_character(base, candidate):
    return base[3] == candidate[3]

  def match_character_and_quote_length(base, candidate):
    return (base[3] == candidate[3] and 0 <= (MQuote.word_count(base[4]) - MQuote.word_count(candidate[4])) <= 0)

  def match_character_and_constant_quote_length(base, candidate):
    return (base[3] == candidate[3] and 5 <= MQuote.word_count(base[4]) <= 7 and 5 <= MQuote.word_count(candidate[4]) <= 7)

  match_dict = { 
    'match_character' : match_character,
    'match_character_and_quote_length': match_character_and_quote_length,
    'match_character_and_constant_quote_length': match_character_and_constant_quote_length
  }
  
  # Start of Real Functions
  
  def __init__(self, dbfilename, quote_type='full', query_type='movie_title'):
    super(MDbQuotes,self).__init__(dbfilename)
    self.c.execute('SELECT id, conv_id, movie, actor, quote, result FROM quotes WHERE quote_type=? AND query_type=? ORDER BY id ASC', (quote_type, query_type))
    self.quotes = self.c.fetchall()
    self.qhash, self.qid_pos, self.q_pos = {}, {}, {}
    for i,q in enumerate(self.quotes):
      self.qhash[q[4]] = i
  
  # RESETS positive quotes before setting them
  def set_positive_quotes(self, pqs, min_results=None):
    self.q_pos, self.qid_pos = {}, {}
    for p in pqs:
      if p in self.qhash:
        if min_results:
          if self.quotes[self.qhash[p]][5] >= min_results:
            self.q_pos[p] = True
            self.qid_pos[self.qhash[p]] = True
        else:
          self.q_pos[p] = True
          self.qid_pos[self.qhash[p]] = True
      else:
        print "Warning: Quote '%s' not found in %s" % (p, self.filename)
  
  # Automatically eliminate positive quotes which have no pairings
  def get_pos_neg_pairs(self, distance=10, found_limit=None, matcher='match_character'):
    pairs = []
    for pos_id in self.qid_pos:
      matches = self.get_nearby_actor_line_ids(pos_id, distance, found_limit, matcher)
      if len(matches) > 0:
        pairs.append((self.quotes[pos_id], [self.quotes[match] for match in matches]))
    return pairs

  # Stop searching if we encounter another positive quote when looking up and down
  def get_nearby_actor_line_ids(self, line_id, distance=10, found_limit=None, matcher='match_character'):
    matcher = MDbQuotes.match_dict[matcher]
    if found_limit:
      matches, found = [], 0
      encountered_pos_up, encountered_pos_down = False, False # When to stop looking up or down
      for i in range(1, distance+1):
        if (encountered_pos_up and encountered_pos_down) or found == found_limit:
          break
        if not encountered_pos_up and line_id - i >= 0 and matcher(self.quotes[line_id],self.quotes[line_id-i]):
          if line_id-i in self.qid_pos:
            encountered_pos_up = True
          elif found < found_limit:
            found += 1
            matches.append(line_id-i)
        if not encountered_pos_down and line_id + i < len(self.quotes) and matcher(self.quotes[line_id],self.quotes[line_id+i]):
          if line_id+i in self.qid_pos:
            encountered_pos_down = True
          elif found < found_limit:
            found += 1
            matches.append(line_id+i)
      return matches
    else:
      matches = []
      encountered_pos_up, encountered_pos_down = False, False # When to stop looking up or down
      for i in range(1, distance+1):
        if encountered_pos_up and encountered_pos_down:
          break
        if not encountered_pos_up and line_id - i >= 0 and matcher(self.quotes[line_id],self.quotes[line_id-i]):
          if line_id-i in self.qid_pos:
            encountered_pos_up = True
          else:
            matches.append(line_id-i)
        if not encountered_pos_down and line_id + i < len(self.quotes) and matcher(self.quotes[line_id],self.quotes[line_id+i]):
          if line_id+i in self.qid_pos:
            encountered_pos_down = True
          else:
            matches.append(line_id+i)
      return matches

def sql_ins(c, conv_id, movie_name, actor, quote, quote_type, query_type, result, urls, engine='bing'):
  c.execute('INSERT INTO quotes (conv_id, movie, actor, quote, source, quote_type, query_type, result, urls) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)', (conv_id, movie_name, actor, quote, engine, quote_type, query_type, result, urls))
