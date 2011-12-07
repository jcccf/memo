import sqlite3, os.path, MySQLdb
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

  def i(self, query):
    self.c.execute(query)
    return self.c
  
  def it(self, query, tuples):
    self.c.execute(query, tuples)
    return self.c
    
  def commit(self):
    self.conn.commit()
  
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

class MMySQLDb(MDb):
  def __init__(self, database, host='lion.cs.cornell.edu', username='jc882', password='memo3330'):
    self.conn = MySQLdb.connect(host, username, password, database)
    self.conn.text_factory = str
    self.c = self.conn.cursor()
    

class MMySQLDbQuotes(MMySQLDb):

  # Helper Match Functions

  def match_character(base, candidate):
    return base[MMySQLDbQuotes.ACTOR] == candidate[MMySQLDbQuotes.ACTOR]

  def match_imdb_character_and_quote_length(length):
    return (lambda base, candidate: (base[MMySQLDbQuotes.ACTOR] == candidate[MMySQLDbQuotes.ACTOR] and -length <= base[MMySQLDbQuotes.IMDB_QUOTE_WC] - candidate[MMySQLDbQuotes.QUOTE_WC] <= length))
    
  def match_imdb_character_and_constant_quote_length(minl,maxl):
    return (lambda base, candidate: (base[MMySQLDbQuotes.ACTOR] == candidate[MMySQLDbQuotes.ACTOR] and minl <= base[MMySQLDbQuotes.IMDB_QUOTE_WC] <= maxl and minl <= candidate[MMySQLDbQuotes.QUOTE_WC] <= maxl))

  match_dict = { 
    'match_character' : match_character,
    'match_character_imdb_and_quote_length1': match_imdb_character_and_quote_length(1),
    'match_character_imdb_and_quote_length3': match_imdb_character_and_quote_length(3),
    'match_character_imdb_and_quote_length5': match_imdb_character_and_quote_length(5),
    'match_character_imdb_and_quote_length7': match_imdb_character_and_quote_length(7),
    'match_character_imdb_and_quote_length9': match_imdb_character_and_quote_length(9),
    'match_character_imdb_and_quote_length11': match_imdb_character_and_quote_length(11),
    'match_character_imdb_and_constant_quote_length': match_imdb_character_and_constant_quote_length(5,7)
  }

  # Start of Real Functions

  ID = 0
  CONV_ID = 1
  ACTOR = 2
  IS_MEMO = 3
  QUOTE = 4
  QUOTE_WC = 5
  RESULT = 6
  IMDB_QUOTE = 7
  IMDB_QUOTE_WC = 8
  IMDB_RESULT = 9

  def __init__(self, database, movie_name, quote_type='full', query_type='movie_title'):
    super(MMySQLDbQuotes,self).__init__(database)
    self.c.execute('SELECT id, conv_id, actor, is_memorable, quote, quote_wc, result_fixed, imdb_quote, imdb_quote_wc, imdb_result_fixed FROM quotes WHERE movie_name=%s AND quote_type=%s AND query_type=%s ORDER BY id ASC', (movie_name, quote_type, query_type))
    self.quotes = self.c.fetchall()
    self.qhash, self.qid_pos, self.q_pos = {}, {}, {}
    for i,q in enumerate(self.quotes):
      self.qhash[q[MMySQLDbQuotes.QUOTE]] = i

  def get_pos_neg_pairs(self, imdb_memorability=True, pos_min_wc=0, pos_min_char=35, pos_min_results=10, pos_max_results=100000, neg_max_results=10, distance=50, found_limit=1, matcher='match_character'):
    '''Automatically eliminate positive quotes which have no pairings'''
    # Set positive quotes
    self.q_pos, self.qid_pos = {}, {}
    ignore_memorability = True if imdb_memorability is not True else False
    for q in self.quotes:
      if (ignore_memorability or q[MMySQLDbQuotes.IS_MEMO] == 1) and pos_max_results >= q[MMySQLDbQuotes.IMDB_RESULT] >= pos_min_results and len(q[MMySQLDbQuotes.IMDB_QUOTE]) >= pos_min_char and q[MMySQLDbQuotes.IMDB_QUOTE_WC] >= pos_min_wc:
        self.q_pos[q[MMySQLDbQuotes.QUOTE]] = True
        self.qid_pos[self.qhash[q[MMySQLDbQuotes.QUOTE]]] = True
        
    # Find negative quotes that pair with the positive quotes
    pairs = []
    for pos_id in self.qid_pos:
      matches = self.get_nearby_actor_line_ids(pos_id, neg_max_results, distance, found_limit, matcher)
      if len(matches) > 0:
        pairs.append((self.quotes[pos_id], [self.quotes[match] for match in matches]))
    return pairs

  # Stop searching if we encounter another positive quote when looking up and down
  def get_nearby_actor_line_ids(self, line_id, neg_max_results=10, distance=50, found_limit=1, matcher='match_character'):
    matcher = MMySQLDbQuotes.match_dict[matcher]
    matches, found = [], 0
    encountered_pos_up, encountered_pos_down = False, False # When to stop looking up or down
    for i in range(1, distance+1):
      if (encountered_pos_up and encountered_pos_down) or found == found_limit:
        break
      if not encountered_pos_up and line_id - i >= 0 and matcher(self.quotes[line_id],self.quotes[line_id-i]):
        #print "Looking up at ", self.quotes[line_id-i][4]
        if line_id-i in self.qid_pos:
          encountered_pos_up = True
        elif found < found_limit and self.quotes[line_id-i][MMySQLDbQuotes.RESULT] <= neg_max_results:
          found += 1
          matches.append(line_id-i)
      if not encountered_pos_down and line_id + i < len(self.quotes) and matcher(self.quotes[line_id],self.quotes[line_id+i]):
        #print "Looking down at ", self.quotes[line_id+i][4]
        if line_id+i in self.qid_pos:
          encountered_pos_down = True
        elif found < found_limit and self.quotes[line_id+i][MMySQLDbQuotes.RESULT] <= neg_max_results:
          found += 1
          matches.append(line_id+i)
    return matches

def sql_ins(c, conv_id, movie_name, actor, quote, quote_type, query_type, result, urls, engine='bing'):
  c.execute('INSERT INTO quotes (conv_id, movie, actor, quote, source, quote_type, query_type, result, urls) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)', (conv_id, movie_name, actor, quote, engine, quote_type, query_type, result, urls))
