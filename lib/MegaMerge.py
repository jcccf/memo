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
    `source` varchar(255) DEFAULT NULL,
    `quote_type` varchar(255) DEFAULT NULL,
    `query_type` varchar(255) DEFAULT NULL,
    `result` bigint(20) DEFAULT NULL,
    `result_fixed` bigint(20) DEFAULT NULL,
    `urls` text,
    PRIMARY KEY (`id`)
  ) ENGINE=MyISAM DEFAULT CHARSET=utf8;''')
  merge_db.q('''CREATE TABLE `memorable` (
    `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
    `movie_name` varchar(255) DEFAULT NULL,
    `imdb_quote` text,
    `matched_quote` text,
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
  
def load_imdb_memorable(dbname):
  """Load Positive Examples of Quotes"""
  pos = MFile.pickle_load_mac('../data/pn2/poslinesdict2.newdata.pickle')
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
  
def load_movies(dbname):
  """Load Movies from Individual Files"""
  merge_db = MDb.MMySQLDb(dbname)
  for script_filename in MFile.glob_filenames('../data/scripts/db/*.bing.sqlite'):
    movie_name = MQuote.clean_movie_title(script_filename.split('.',1)[0])
    print "Doing %s..." % movie_name
    mdb = MDb.MDb('../data/scripts/db/%s' % script_filename)
    quotes = mdb.q('SELECT conv_id, movie, actor, quote, source, quote_type, query_type, result, urls FROM quotes ORDER BY id ASC')
    mdb.close()
    for conv_id, movie, actor, quote, source, quote_type, query_type, result, urls in quotes:
      is_memorable = 0
      merge_db.qt('INSERT INTO quotes (conv_id, movie_name, movie, actor, is_memorable, quote, source, quote_type, query_type, result, urls) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)', (conv_id, movie_name, movie, actor, is_memorable, quote, source, quote_type, query_type, result, urls))
    merge_db.commit()
  merge_db.close()
      
def label_memorable_quotes(dbname):
  merge_db = MDb.MMySQLDb(dbname)
  print 'Getting IDs to Update...'
  ids = merge_db.q("SELECT q.id FROM quotes as q, memorable as m WHERE q.movie_name = m.movie_name AND q.quote = m.matched_quote AND q.quote_type='full'")
  print 'Updating IDs...'
  for id in ids:
    merge_db.qt('UPDATE quotes SET is_memorable = 1 WHERE id = %s', (id))
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
  merge_db.qt('UPDATE quotes SET result_fixed = result')
  merge_db.commit()
  merge_db.close()
    
def populate_fixed_results(dbname):
  merge_db = MDb.MMySQLDb(dbname)
  print 'Populating Fixed Results...'
  random_results = merge_db.q("SELECT movie_name, AVG(result) as avg_result FROM random_quotes WHERE query_type='movie_title' OR query_type='movie_title_2' GROUP BY movie_name")
  for movie_name, avg_result in random_results:
    print '\t%s' % movie_name
    low_res, hi_res = 0.7*float(avg_result), 1.3*float(avg_result)
    candidates = merge_db.qt('SELECT id, quote FROM quotes WHERE movie_name=%s AND query_type=\'movie_title\' AND result < %s AND result > %s', (movie_name, hi_res, low_res))
    for candidate_id, quote in candidates:
      if len(quote) > 50:
        merge_db.qt('UPDATE quotes SET result_fixed=%s WHERE id=%s', (0,candidate_id))

def generate_csv_from_db(dbname, filename):
  merge_db = MDb.MMySQLDb(dbname)
  quotes = merge_db.q("SELECT movie_name, actor, is_memorable, result, quote, query_type FROM quotes WHERE quote_type='full' ORDER BY id ASC")
  with open(filename, 'w') as f:
    last_movie_name, line_no, last_result = '', 1, 0
    for movie_name, actor, is_memorable, result, quote, query_type in quotes:
      if last_movie_name != movie_name and query_type == 'plain':
        line_no = 1
        last_movie_name = movie_name
      if query_type == 'plain':
        last_result = result
        line_no += 1
      else:
        f.write("%s %d %s %d %d %d %s\n" % (movie_name.replace(' ', '_'), line_no, actor, is_memorable, result, last_result, quote))

DBNAME = 'memo'
prepare_schema(DBNAME)
load_imdb_memorable(DBNAME)
load_movies(DBNAME)
label_memorable_quotes(DBNAME)
import_random_quotes(DBNAME, ['../data/scripts/db/names.bing.sqlite', '../data/scripts/db/names_cham_unique_dedup.bing.sqlite'])
populate_fixed_results(DBNAME)
# generate_csv_from_db(DBNAME, '../data/merged/posneg2.txt')
