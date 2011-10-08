from collections import defaultdict
import sqlite3, nltk, unidecode, pickle
from misc import *
from parsers.Bing import *
BASE = '../data/chameleon/'

app_id = 1
MOVIES = BASE+'movie_titles_metadata.txt'
LINES = BASE+'movie_lines.txt'
CONVS = BASE+'movie_conversations.txt'

PARSED_MOVIES = '../data/scripts/names_old.txt'

PARSED_RESULT = '../data/scripts/names_old_comp.pickle'

movies = []
with open(MOVIES,'r') as f:
  for l in f:
    mid, name, _ = l.split(' +++$+++ ', 2)
    movies.append(unidecode.unidecode(name))
    
pmovies = []
with open(PARSED_MOVIES,'r') as f:
  for l in f:
    _, name = l.replace('\n','').split('\t\t')
    pmovies.append(name)
    
pn = []
for p in pmovies:
  if ", the" in p:
    p = 'the ' + p.replace(', the', '')
  pn.append(p)
pmovies = pn

i = 0
mresult = []
for p in pmovies:
  a = min([(b, nltk.metrics.edit_distance(p,b)) for b in movies], key=lambda x: x[1])
  mresult.append((p, a[0], a[1]))
  if a[1] < 5:
    i += 1

print float(i)/len(pmovies)

pickle.dump(mresult, open(PARSED_RESULT,'w'))