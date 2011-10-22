import sqlite3, pickle, unidecode
import matplotlib.pyplot as plt
import matplotlib
from plot import *
from misc import *

BASEDIR = '../data/pn2/db'
POSFILE = 'poslinesdict.newdata'
NEGFILE = 'negativelinesdict.newdata'

# Prepare Movie Hash
movies, movie_list = {}, ['-']
def get_movie_id(name):
  if name in movies:
    return movies[name]
  else:
    get_movie_id.counter += 1
    movies[name] = get_movie_id.counter
    movie_list.append(name)
    return get_movie_id.counter
get_movie_id.counter = 0

def make_xy(filename):
  x, y = [], []
  db = MDb.MDb('%s/%s.bing.sqlite' % (BASEDIR, filename))
  rs = db.q('SELECT movie, result FROM quotes WHERE quote_type=\'full\' AND query_type=\'movie_title\'')
  for movie_name, result in rs:
    x.append(result)
    y.append(get_movie_id(movie_name))
  return (x, y)

# Load Positive Examples
x_pos, y_pos = make_xy(POSFILE)
x_neg, y_neg = make_xy(NEGFILE)

l = []
plt.clf()
plt.figure().set_size_inches(10,80)
plt.axes([0.15, 0.02, 0.8, 0.96])
l.append(plt.scatter(x_pos, y_pos, c='green', edgecolors='none', alpha=0.5))
l.append(plt.scatter(x_neg, y_neg, c='red', edgecolors='none', alpha=0.5))
plt.legend(l, ['Positive (IMDB Memo)', 'Negative'], loc='best')
plt.xlim((-1,60))
plt.ylim((0,len(movie_list)))
plt.xlabel('# of results')
plt.yticks(range(len(movie_list)), movie_list, fontsize=8)
plt.grid(True)
plt.savefig('hello.png')

x_pos = [x for x in x_pos if x < 100]
x_neg = [x for x in x_neg if x < 100]
DistributionPlot.histogram_plot('hello2.png', [x_pos,x_neg], bins=100, normed=0, color=['green', 'red'], label=['pos','neg'], histtype='bar', ylabel='Frequency', xlabel='# of results returned')