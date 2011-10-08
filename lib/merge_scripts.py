import nltk, string, pickle, sqlite3, re, unidecode, os.path, shutil
from parsers import *
from misc import *

def parse_scriptnames(filename):
  ns, nsp, nspo = [], [], []
  with open(filename, 'r') as f:
    for l in f:
      a, b = l.replace('\n','').split('\t\t')
      ns.append(a)
      nspo.append(b)
      b = b.replace(', the','').replace('the ','')
      b = re.sub('[%s]' % re.escape(string.punctuation), '', b.lower())
      nsp.append(b)
  return (ns, nsp, nspo)
  
ns, nsp, nspo = parse_scriptnames('../data/scripts/names_old.txt')
cs, csp, cspo = parse_scriptnames('../data/chameleon/names_cham.txt')

N_PREFIX = '../data/scripts/'
C_PREFIX = '../data/chameleon/processed2/'

matches = sorted(set(nsp) & set(csp))

matchfile = []
matchless = []
for a, b, c in zip(cs, csp, cspo):
  c = c.replace(', the','')
  if b in matches:
    matchfile.append((a,c))
  else:
    matchless.append((a,c))
    
with open('../data/chameleon/names_cham_dups.txt', 'w') as f:
  for s, t in matchfile:
    f.write('%s\t\t%s\n' % (s, t))    

with open('../data/chameleon/names_cham_uniques.txt', 'w') as f:
  for s, t in matchless:
    f.write('%s\t\t%s\n' % (s, t))
    shutil.copy2('../data/chameleon/processed2/'+s+'.txt', '../data/chameleon/processed2_unique/'+s+'.txt')
    shutil.copy2('../data/chameleon/processed2/'+s+'.pickle', '../data/chameleon/processed2_unique/'+s+'.pickle')