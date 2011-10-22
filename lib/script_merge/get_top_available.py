import nltk, string, pickle, sqlite3, re, unidecode
from parsers import *
from misc import *

names = []
with open('../data/scripts/names_top.txt', 'r') as f:
  i = 0
  for l in f:
    if i % 4 == 2:
      n = unidecode.unidecode(l).replace('\n','').lower()
      n = re.sub(r'\s*\([0-9]+\)', '', n)
      n = re.sub('[%s]' % re.escape(string.punctuation), '', n)
      n = n.replace('the ', '')
      names.append(n)
    i += 1

#print sorted(names)

done = []
with open('../data/scripts/names_top_20.txt', 'r') as f:
  for l in f:
    done.append(l.split('\t\t')[0])
with open('../data/scripts/names_top_40.txt', 'r') as f:
  for l in f:
    done.append(l.split('\t\t')[0])
with open('../data/scripts/names_top_60.txt', 'r') as f:
  for l in f:
    done.append(l.split('\t\t')[0])


ns, nsp, nspo = [], [], []
with open('../data/scripts/names_old.txt', 'r') as f:
  for l in f:
    a, b = l.replace('\n','').split('\t\t')
    if a not in done:
      ns.append(a)
      nspo.append(b)
      b = b.replace(', the','').replace('the ','')
      b = re.sub('[%s]' % re.escape(string.punctuation), '', b.lower())
      nsp.append(b)

#print sorted(nsp)

matches = sorted(set(names) & set(nsp))

matchfile = []
matchless = []
for a, b, c in zip(ns, nsp, nspo):
  c = c.replace(', the','')
  if b in matches:
    matchfile.append((a,c))
  else:
    matchless.append((a,c))
    
with open('../data/scripts/names_top_250.txt', 'w') as f:
  for s, t in matchfile:
    f.write('%s\t\t%s\n' % (s, t))    

with open('../data/scripts/names_rest.txt', 'w') as f:
  for s, t in matchless:
    f.write('%s\t\t%s\n' % (s, t))