from scikits.learn import svm, linear_model
import sqlite3, random, nltk
from misc.MQuote import *

MOVIE = 'star_wars_a_new_hope'
db_file = '../data/scripts/db/%s.sqlite' % MOVIE
memo_lower = '../data/scripts/memo/%s_lower10.txt' % MOVIE
memo_upper = '../data/scripts/memo/%s_upper10.txt' % MOVIE

def load_quotes(db_file):
  conn = sqlite3.connect(db_file)
  conn.text_factory = str
  c = conn.cursor()
  c.execute('SELECT actor, quote, min(result) FROM quotes WHERE quote_type=\'full\' GROUP BY quote, movie ORDER BY id asc')
  return c.fetchall()
  
# Rank by upper and lower %
def lower_and_upper(percent, quotes):
  s = sorted(quotes, key=lambda x: x[2])
  threshold = int(len(s) * float(percent))
  lower = s[:threshold]
  upper = s[-threshold:]
  return (lower, upper)

def q_to_file(quotes, filename):
  with open(filename, 'w') as f:
    for a,l,_ in quotes:
      f.write(a+"\t\t"+l+"\n")

quotes = load_quotes(db_file)
lower, upper = lower_and_upper(0.1, quotes)
q_to_file(lower, memo_lower)
q_to_file(upper, memo_upper)

def prev_next_quote(i):
  l, u = i-1, i+1
  actor = quotes[i][0]
  while (l >= 0):
    if quotes[l][0] == actor:
      break
    l -= 1
  while (u < len(quotes)):
    if quotes[u][0] == actor:
      break;
    u += 1
  lq = l > 0 and quotes[l] or None
  uq = u < len(quotes) and quotes[u] or None
  return (lq, uq)
  
# Load IMDB Quotes
base = []
with open('../data/scripts/star_wars_imdb.txt') as f:
  base = f.readlines()
base = [s.replace('\n','') for s in base]
  
# Do Upper and Lower
for n in range(1, 8):
  print "Computing n = %d" % n
  lower, upper = lower_and_upper(float(n)/10,quotes)
  uandl = []
  for i in range(1, len(quotes)-1):
    lq, uq = prev_next_quote(i)
    #print lq, quotes[i], uq
    if quotes[i] in upper and lq in lower: # and uq in upper:
      uandl.append(quotes[i])
  q_to_file(uandl, '../data/scripts/memo/%s_r_ual_%d.txt' % (MOVIE,n))
  # print uandl
  uandl_f = filter_by_length_flat(uandl, 1, 4, 15)
  #print uandl_f
  q_to_file(uandl_f, '../data/scripts/memo/%s_r_ulf_%d.txt' % (MOVIE,n))
  
  edist = 0
  for __,l,_ in uandl:
    edist += min([nltk.metrics.edit_distance(l,b) for b in base])
  print (edist / float(len(uandl)))
  
  edist = 0
  for __,l,_ in uandl_f:
    edist += min([nltk.metrics.edit_distance(l,b) for b in base])
  print (edist / float(len(uandl_f)))

print "NOW FOR RATIO"

# Now Do Ratio
for n in range(1, 6):
  for m in range(0, 3):
    print "Computing %d %d..." % (n,m)
    memo = []
    for i in range(1, len(quotes)-1):
      r1 = quotes[i][2]
      lq, uq = prev_next_quote(i)
      if lq is not None and uq is not None and r1 * word_count(quotes[i][1]) ** m > n * lq[2] * word_count(lq[1]) ** m: # and r1 > n * uq[2]:
        memo.append(quotes[i])
    q_to_file(memo, '../data/scripts/memo/%s_r_rel_%d_%d.txt' % (MOVIE,n,m))
    memo_f = filter_by_length_flat(memo, 1, 4, 15)
    #memo_f = filter(lambda (_,r): r > 5000, memo_f)
    q_to_file(memo_f, '../data/scripts/memo/%s_r_rlf_%d_%d.txt' % (MOVIE,n,m))
    edist = 0
    for __,l,_ in memo:
      edist += min([nltk.metrics.edit_distance(l,b) for b in base])
    print (edist / float(len(memo)))
    edist = 0
    for __,l,_ in memo_f:
      edist += min([nltk.metrics.edit_distance(l,b) for b in base])
    print (edist / float(len(memo_f)))