import nltk, string, pickle, sqlite3, re, unidecode, os.path
from parsers import *
from misc import *

PREFIX = '../data/chameleon/processed/'
OUT_PREFIX = '../data/chameleon/processed2/'

a = pickle.load(open('../data/chameleon/real_name.afterduplications.pickle','rb'))

def num_quotes(convs):
  l = 0
  for c in convs:
    l += len(c)
  return l

def process_script(filename):
  convs, conv = [], []
  with open(filename,'r') as f:
    for l in f:
      l = l.replace('\n', '')
      if len(l) == 0:
        if len(conv) > 0:
          convs.append(conv)
          conv = []
        continue
      actor, quote = l.split(':', 1)
      conv.append((actor,quote))
  return convs

def write_script(out, filename, filename_pickle):
  with open(filename, 'w') as f:
    for conv in out:
      f.write("\n---\n\n")
      for actor,quote in conv:
        f.write(actor + ":\n" + quote + "\n")
  pickle.dump(out, open(filename_pickle, 'w'))

valids = []
for filename, movie_name in a.iteritems():
  if os.path.exists(PREFIX+filename+'.txt') and len(movie_name) > 0:
    # Now test if is a valid processed script
    script = process_script(PREFIX+filename+'.txt')
    if num_quotes(script) > 100:
      mn = unidecode.unidecode(movie_name)
      mn_filename = mn.replace(' ','_').replace('/',' ')
      print OUT_PREFIX+mn_filename+'.txt'
      write_script(script, OUT_PREFIX+mn_filename+'.txt', OUT_PREFIX+mn_filename+'.pickle')
      valids.append((mn_filename,mn))

with open('../data/chameleon/names_cham.txt', 'w') as f:
  for s, t in valids:
    f.write('%s\t\t%s\n' % (s, t))
        
#write_script(process_script('../data/chameleon/processed/8mm.txt'), '../data/chameleon/test.txt')