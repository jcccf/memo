from collections import defaultdict
import math, operator

def average_tuples(setsoftuples):
  '''Given (k,v) tuples, return (k,average of v) tuples'''
  dict_accum = {}
  for tuples in setsoftuples:
    for k,v in tuples:
      if k in dict_accum:
        dict_accum[k] += v
      else:
        dict_accum[k] = v
  return [(k,v/len(setsoftuples)) for k, v in dict_accum.iteritems()]
  
def print_tuples(tuples, filename):
  with open(filename, 'w') as f:
    for a,b in tuples:
      f.write('{}\t{}\n'.format(a,b))

# Creates Vectors from Sets of Documents
# Most Useful for Text Documents
class MagicVectorizer(object):
  def __init__(self):
    self.dicty = {}
    self.doc_frequency = {}
    self.counter = 1
    self.doc_count = 0.0
    
  # Add a document, which is an object array
  def add(self, document):
    self.doc_count += 1
    seen = []
    for term in document:
      if not term in seen:
        if term in self.dicty:
          self.doc_frequency[self.dicty[term]] += 1
        else:
          self.dicty[term] = self.counter
          self.doc_frequency[self.counter] = 1
          self.counter += 1
        seen.append(term)

  # Return the vector that corresponds to the input document
  # Set text to true to return a SVMLight compatible output string
  # Set tfidf to true to return tf-idf instead of term frequency
  def vectorize(self, document, text=False, tfidf=False):
    vect = defaultdict(int)
    for term in document:
      vect[self.dicty[term]] += 1
    if tfidf:
      vec2 = {}
      for k,v in vect.iteritems():
        vec2[k] = v * math.log(self.doc_count/self.doc_frequency[k])
      vect = vec2
    vect = sorted(vect.items(), key=lambda (k,v): k)
    if text:
      if tfidf:
        return ''.join(['%d:%f ' % (k,v) for k,v in vect])[:-1]
      else:
        return ''.join(['%d:%d ' % (k,v) for k,v in vect])[:-1]
    else:
      return vect
      
  def dictionary_tofile(self, filename):
    '''Output dicty to file with index, dictionary_word on each line'''
    vs = sorted(self.dicty.iteritems(), key=operator.itemgetter(1))
    with open(filename, 'w') as f:
      for word, i in vs:
        f.write('%d\t%s\n' % (i, word))
  
  def decode_tuples(self, tuples):
    '''Given (dict_val,x) tuples, return (dict_key,x) tuples'''
    dicty_rev = dict(zip(self.dicty.values(), self.dicty.keys())) # swap keys and values
    return [(dicty_rev[i], v) for i,v in tuples]
    
# a = MagicVectorizer()
# a.add(['hello','world'])
# a.add(['bye','world'])
# print a.vectorize(['hello', 'world', 'world'], text=True)