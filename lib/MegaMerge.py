from misc import *
import unidecode, os.path, sqlite3, pickle, operator
from collections import defaultdict

def prepare_schema(dbname):
  merge_db = MDb.MMySQLDb(dbname)
  merge_db.q('''DROP TABLE IF EXISTS `memorable`;''')
  merge_db.q('''DROP TABLE IF EXISTS `quotes`;''')
  merge_db.q('''DROP TABLE IF EXISTS `random_quotes`''')
  merge_db.q('''CREATE TABLE `quotes` (
    `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
    `conv_id` int(11) unsigned DEFAULT NULL,
    `movie_name` varchar(255) DEFAULT NULL,
    `movie` varchar(255) DEFAULT NULL,
    `actor` varchar(255) DEFAULT NULL,
    `is_memorable` tinyint(1) DEFAULT NULL,
    `quote` text,
    `quote_wc` smallint(2) DEFAULT NULL, 
    `source` varchar(255) DEFAULT NULL,
    `quote_type` varchar(255) DEFAULT NULL,
    `query_type` varchar(255) DEFAULT NULL,
    `result` bigint(20) DEFAULT NULL,
    `result_fixed` bigint(20) DEFAULT NULL,
    `imdb_quote` text,
    `imdb_quote_wc` smallint(2) DEFAULT NULL,
    `imdb_result_fixed` bigint(20) DEFAULT NULL,
    `urls` text,
    PRIMARY KEY (`id`)
  ) ENGINE=MyISAM DEFAULT CHARSET=utf8;''')
  merge_db.q('''CREATE TABLE `memorable` (
    `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
    `movie_name` varchar(255) DEFAULT NULL,
    `imdb_quote` text,
    `matched_quote` text,
    `query_type` varchar(255) DEFAULT NULL,
    `result` bigint(20) DEFAULT NULL,
    `result_fixed` bigint(20) DEFAULT NULL,
    `urls` text,
    PRIMARY KEY (`id`)
  ) ENGINE=MyISAM DEFAULT CHARSET=utf8;''')
  merge_db.q('''CREATE TABLE `multilines` (
    `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
    `conv_id` int(11) unsigned DEFAULT NULL,
    `movie_name` varchar(255) DEFAULT NULL,
    `actor` varchar(255) DEFAULT NULL,
    `quote` text,
    `quote_wc` smallint(2) DEFAULT NULL,
    `quote_type` varchar(255) DEFAULT NULL,
    `query_type` varchar(255) DEFAULT NULL,
    `result` bigint(20) DEFAULT NULL,
    `result_fixed` bigint(20) DEFAULT NULL,
    `urls` text,
    PRIMARY KEY (`id`)
  ) ENGINE=MyISAM DEFAULT CHARSET=utf8;''')
  merge_db.q('''CREATE TABLE `random_quotes` (
    `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
    `movie_name` varchar(255) DEFAULT NULL,
    `movie` varchar(255) DEFAULT NULL,
    `quote` text,
    `source` varchar(255) DEFAULT '',
    `query_type` varchar(255) DEFAULT NULL,
    `result` bigint(20) DEFAULT NULL,
    PRIMARY KEY (`id`)
  ) ENGINE=MyISAM DEFAULT CHARSET=utf8;''')
  merge_db.commit()
  merge_db.close()
  print 'Prepared Database Schema for %s' % dbname
  
# Fast
def load_imdb_memorable(dbname):
  """Load Positive Examples of Quotes"""
  pos = MFile.pickle_load_mac('../data/pn2/poslinesdict2.newmatch.111611.pickle')
  pos2 = {}
  for k, v in pos.iteritems():
    vm = [(x[1],x[2]) for x in v]
    pos2[MQuote.clean_movie_title(k)] = vm
  merge_db = MDb.MMySQLDb(dbname)
  for movie_name, quote_pairs in sorted(pos2.iteritems(), key=operator.itemgetter(0)):
    for matched, imdb in quote_pairs:
      merge_db.qt("INSERT INTO memorable (movie_name, imdb_quote, matched_quote) VALUES(%s, %s, %s)", (movie_name, imdb, matched))
  merge_db.commit()
  merge_db.close()
  print "Loaded Memorable Quotes"
  
# Not too slow
def load_imdb_memorable_results(dbname):
  merge_db = MDb.MMySQLDb(dbname)
  mdb = MDb.MDb('../data/pn2/db/poslinesdict2.newmatch.111511.bing.sqlite')
  results = mdb.q('SELECT movie, quote, result, urls FROM quotes WHERE query_type=\'movie_title\' AND quote_type=\'full\'')
  for movie_name, quote, result, urls in results:
    merge_db.qt('UPDATE memorable SET query_type=%s, result=%s, urls=%s WHERE movie_name=%s AND imdb_quote=%s', ('movie_title', result, urls, movie_name, quote))
  merge_db.commit()
  merge_db.close()
  mdb.close()
  
def load_movies(dbname):
  """Load Movies from Individual Files"""
  merge_db = MDb.MMySQLDb(dbname)
  for script_filename in MFile.glob_filenames('../data/scripts/db/*.bing.sqlite'):
    movie_name = MQuote.clean_movie_title(script_filename.split('.',1)[0])
    if movie_name in ["names", "names thes", "names merged", "poslinesdict", "names cham unique dedup"]:
      continue
    print "Doing %s..." % movie_name
    mdb = MDb.MDb('../data/scripts/db/%s' % script_filename)
    quotes = mdb.q('SELECT conv_id, movie, actor, quote, source, quote_type, query_type, result, urls FROM quotes ORDER BY id ASC')
    mdb.close()
    for conv_id, movie, actor, quote, source, quote_type, query_type, result, urls in quotes:
      is_memorable = 0
      quote = MQuote.remove_brackets(quote)
      merge_db.qt('INSERT INTO quotes (conv_id, movie_name, movie, actor, is_memorable, quote, quote_wc, source, quote_type, query_type, result, urls) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)', (conv_id, movie_name, movie, actor, is_memorable, quote, MQuote.word_count(quote), source, quote_type, query_type, result, urls))
    merge_db.commit()
  print 'Creating Index on movie_name...'
  merge_db.q('CREATE INDEX quotes_movie_name ON quotes (movie_name)')
  merge_db.commit()
  merge_db.close()
      
# Not too slow
def label_memorable_quotes(dbname):
  merge_db = MDb.MMySQLDb(dbname)
  print 'Getting IDs to Update for Memorable Quotes...'
  ids = merge_db.q("SELECT q.id FROM quotes as q, memorable as m WHERE q.movie_name = m.movie_name AND q.quote = m.matched_quote AND q.quote_type='full'")
  print 'Updating IDs...'
  for id in ids:
    merge_db.qt('UPDATE quotes SET is_memorable = 1 WHERE id = %s', (id))
  merge_db.commit()
  merge_db.close()
  
# Not too slow
def add_memorable_quotes_to_main_table(dbname):
  print 'Adding IMDB Memorable Quotes to Quotes Table...'
  merge_db = MDb.MMySQLDb(dbname)
  ids = merge_db.q("SELECT q.id, m.imdb_quote, m.result_fixed FROM quotes as q, memorable as m WHERE q.is_memorable = 1 AND q.quote=m.matched_quote AND q.movie_name=m.movie_name")
  # print ids
  for qid, imdb_quote, result_fixed in ids:
    merge_db.qt("UPDATE quotes SET imdb_quote=%s, imdb_quote_wc=%s, imdb_result_fixed=%s WHERE id=%s", (imdb_quote, MQuote.word_count(imdb_quote), result_fixed, qid))
  merge_db.commit()
  merge_db.close()

def import_random_quotes(dbname, filenames):
  merge_db = MDb.MMySQLDb(dbname)
  print 'Importing Random Quotes...'
  for filename in filenames:
    mdb = MDb.MDb(filename)
    random_quotes = mdb.q('SELECT movie, actor, quote, source, query_type, result FROM quotes')
    for movie, movie_name, quote, source, query_type, result in random_quotes:
      movie_name = MQuote.clean_movie_title(movie_name)
      merge_db.qt('INSERT INTO random_quotes (movie_name, movie, quote, source, query_type, result) VALUES(%s, %s, %s, %s, %s, %s)', (movie_name, movie, quote, source, query_type, result))
    mdb.close()
  merge_db.commit()
  merge_db.close()
    
# Slowest
def populate_fixed_results(dbname, table='quotes', quotecol='quote'):
  merge_db = MDb.MMySQLDb(dbname)
  print 'Setting Initial Result_Fixed'
  merge_db.q('UPDATE '+table+' SET result_fixed = result')
  print 'Populating Fixed Results...'
  random_results = merge_db.q("SELECT movie_name, AVG(result) as avg_result FROM random_quotes WHERE query_type='movie_title' OR query_type='movie_title_2' GROUP BY movie_name")
  for movie_name, avg_result in random_results:
    print '\t%s' % movie_name
    #low_res, hi_res = 0.7*float(avg_result), 1.3*float(avg_result)
    #candidates = merge_db.qt('SELECT id, '+quotecol+' FROM '+table+' WHERE movie_name=%s AND query_type=\'movie_title\' AND result < %s AND result > %s', (movie_name, hi_res, low_res))
    low_res = 0.7*float(avg_result)
    candidates = merge_db.qt('SELECT id, '+quotecol+' FROM '+table+' WHERE movie_name=%s AND query_type=\'movie_title\' AND result > %s', (movie_name, low_res))
    for candidate_id, quote in candidates:
      if len(quote) > 50:
        merge_db.qt('UPDATE '+table+' SET result_fixed=%s WHERE id=%s', (0,candidate_id))

def generate_csv_from_db(dbname, filename):
  merge_db = MDb.MMySQLDb(dbname)
  quotes = merge_db.q("SELECT movie_name, actor, is_memorable, result_fixed, quote, query_type, quote_wc, imdb_quote, imdb_quote_wc, imdb_result_fixed FROM quotes WHERE quote_type='full' ORDER BY id ASC")
  with open(filename, 'w') as f:
    last_movie_name, line_no, last_result = '', 1, 0
    for movie_name, actor, is_memorable, result, quote, query_type, quote_wc, imdb_quote, imdb_quote_wc, imdb_result_fixed in quotes:
      if last_movie_name != movie_name and query_type == 'plain':
        line_no = 1
        last_movie_name = movie_name
      if query_type == 'plain':
        last_result = result
        line_no += 1
      else:
        if imdb_quote is None:
          imdb_quote = ''
        if imdb_quote_wc is None:
          imdb_quote_wc = -1
        if imdb_result_fixed is None:
          imdb_result_fixed = -1
        movie_name = movie_name.replace(' ', '_')
        actor = actor.replace('\t','_').replace(' ','_')
        if len(actor) == 0:
          actor = 'INVALID'
        f.write("%s %d %s %d %d %d %d %d %d %s\t\t%s\n" % (movie_name, line_no, actor, quote_wc, is_memorable, result, last_result, imdb_quote_wc, imdb_result_fixed, quote, imdb_quote))

def generate_multiline_csv_from_db(dbname, filename):
  merge_db = MDb.MMySQLDb(dbname)
  quotes = merge_db.q("SELECT conv_id, movie_name, actor, result_fixed, quote, query_type, quote_wc FROM multilines WHERE quote_type='full' ORDER BY id ASC")
  with open(filename, 'w') as f:
    last_movie_name, last_conv_id, conv_line_no, last_result = '', 0, 1, 0
    for conv_id, movie_name, actor, result, quote, query_type, quote_wc in quotes:
      if (last_movie_name != movie_name or last_conv_id != conv_id) and query_type == 'plain':
        last_conv_id = conv_id
        last_movie_name = movie_name
        conv_line_no = 0
      if query_type == 'plain':
        last_result = result
        conv_line_no += 1
      else:
        movie_name = movie_name.replace(' ', '_')
        actor = actor.replace('\t','_').replace(' ', '_')
        if len(actor) == 0:
          actor = 'INVALID'
        f.write("%s %d %d %d %d %d %s\n" % (movie_name, conv_id, conv_line_no, result, last_result, quote_wc, quote))

def load_imdb_multilines(dbname):
  """Load Movies from Individual Files"""
  print 'Loading Multilines...'
  merge_db = MDb.MMySQLDb(dbname)
  mdb = MDb.MDb('../data/pn2/db/title_to_multiliners.bing.sqlite')
  quotes = mdb.i('SELECT conv_id, movie, actor, quote, quote_type, query_type, result, urls FROM quotes ORDER BY id ASC')
  for conv_id, movie_name, actor, quote, quote_type, query_type, result, urls in quotes:
    quote = MQuote.remove_brackets(quote)
    merge_db.qt('INSERT INTO multilines (conv_id, movie_name, actor, quote, quote_wc, quote_type, query_type, result, urls) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s)', (conv_id, movie_name, actor, quote, MQuote.word_count(quote), quote_type, query_type, result, urls))
  mdb.close()
  merge_db.commit()
  print 'Creating Index on movie_name...'
  merge_db.q('CREATE INDEX multilines_movie_name ON multilines (movie_name)')
  merge_db.commit()
  merge_db.close()

# Temporary use only
def temp_update_wc(dbname):
  merge_db = MDb.MMySQLDb(dbname)
  for qid, quote in merge_db.i('SELECT id, quote FROM quotes'):
    merge_db.qt('UPDATE quotes SET quote_wc=%s WHERE id=%s', (MQuote.word_count(quote), qid))

def temp_update_quotes(dbname):
  merge_db = MDb.MMySQLDb(dbname)
  for qid, quote in merge_db.i('SELECT id, quote FROM quotes'):
    merge_db.qt('UPDATE quotes SET quote=%s WHERE id=%s', (MQuote.remove_brackets(quote), qid))

DBNAME = 'memo'
# prepare_schema(DBNAME)
# load_imdb_memorable(DBNAME)
# load_imdb_memorable_results(DBNAME)
# load_imdb_multilines(DBNAME)
# load_movies(DBNAME)
# label_memorable_quotes(DBNAME)
# import_random_quotes(DBNAME, ['../data/scripts/db/names_merged.bing.sqlite', '../data/scripts/db/names_cham_unique_dedup.bing.sqlite'])
# populate_fixed_results(DBNAME, 'quotes', 'quote')
# populate_fixed_results(DBNAME, 'memorable', 'imdb_quote')
# populate_fixed_results(DBNAME, 'multilines', 'quote')
# add_memorable_quotes_to_main_table(DBNAME)
# generate_csv_from_db(DBNAME, '../data/merged/posneg_20111121_3.txt')
generate_multiline_csv_from_db(DBNAME, '../data/merged/ml_20111201.txt')

# CHECKS
# SELECT * FROM quotes WHERE quote LIKE '%lorem%'