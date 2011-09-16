import nltk, string, re

# Some Regexes
remove_actions = re.compile('(\[.+\])')
remove_actions_2 = re.compile('(\(.+\))')
match_left = re.compile('([^\[])*([\s]*\[[^\[]*)')
match_right = re.compile('([^\]]*\])([\s]*[^\]]*)*')
whitespace = re.compile('([\s]+)')
authorrest = re.compile('([a-zA-Z0-9\\\(\)\-\"\'\/.,\#;\s]+):(.+)')
sentences = re.compile('([^.!?\s][^.!?]*(?:[.!?](?![\'\"]?\s|$)[^.!?]*)*[.!?]?[\'\"]?(?=\s|$))')

# Get Words between MIN and MAX_LENGTH
def filter_by_length(movie_quotes, min_len=5, max_len=7):
  filtered = []
  for movie, quotes in movie_quotes:
    for actor, quote in quotes:
      words = filter(lambda s: s not in string.punctuation, nltk.word_tokenize(quote))
      if min_len <= len(words) <= max_len:
        filtered.append((movie,actor,quote))
  print "%d quotes between %d and %d..." % (len(filtered), min_len, max_len)
  return filtered

# Split a quote into sentences
def split_into_sentences(quote):
  # Split everything into sentences, but...
  subquotes = sentences.split(quote)
  subquotes = filter(lambda s:len(s.strip())>0, subquotes)
  # Now look for Mr. and Mrs. and join them back
  new_squotes = []
  i = 0
  last_quote = ''
  for subquote in subquotes:
    s1, s2, s3 = subquote.rpartition(' ')
    if s1 and ('Mr.' in s3 or 'Mrs.' in s3):
      last_quote += subquote + ' '
    else:
      last_quote += subquote
      new_squotes.append(last_quote)
      last_quote = ''
  new_squotes.append(last_quote)
  return filter(None, new_squotes)

# Clean a quote and remove all actions (things in brackets)
def clean_quote(quote):
  new_quote = remove_actions.sub('', quote)
  if match_left.match(new_quote) :
    txt = match_left.match(new_quote).group(1)
    if txt:
      return txt + " "
    else:
      return " "
  elif match_right.match(new_quote) :
    txt = match_right.match(new_quote).group(2)
    if txt:
      return txt + " "
    else:
      return " "
  else :
    return new_quote + " "

def remove_brackets(quote):
  return remove_actions_2.sub('', remove_actions.sub('',quote)).strip()

# Remove extra whitespace in quotes (ex. multiple spaces)
def whitespace_quote(quote):
  return whitespace.sub(' ', quote).strip()