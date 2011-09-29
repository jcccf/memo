import re, time, random, urllib, urllib2, json, pickle
from QuoteFunctions import *

NAME = 'star_wars_a_new_hope'
URL = 'http://www.imsdb.com/scripts/Star-Wars-A-New-Hope.html'
# NAME = None
# URL = 'http://www.imsdb.com/scripts/Above-the-Law.html'

if not NAME:
  NAME = URL.split('/')[-1].split('.')[0].lower().replace('-','_')

opener = urllib2.build_opener()
try:
  fil = opener.open(URL)
except urllib2.URLError as detail:
  print "Caught URLError: ", detail

text = fil.read()
text = text.split('<td class=scrtext><pre><html><head></head><body>')
if len(text) != 2:
  print "Error: Can't Find Script Part"
text = text[1].split('</pre></table>')
if len(text) != 2:
  print "Error: Can't Find Script Part"
text = text[0]

lines = text.split('\n')

i = 0
mode = "find_bold"
bolded, quote = '', ''
conversations = []
found = []

# Detect Space Type
space_type = None
space_types = ['                         ', '                  ', '          ']
print len(re.findall("</b>%s" % space_types[1], text))

maxfound = 0
for stype in space_types:
  if len(re.findall("</b>%s" % stype, text)) > 200:
    maxfound = len(re.findall("</b>%s" % stype, text))
    space_type = stype
    smaller_space_type = stype[:len(stype)/2]
    break

print len(smaller_space_type)

while i < len(lines):
  l = lines[i]
  if mode == 'find_bold':
    if "<b>" in l:
      bolded = l.split('<b>')[1]
      mode = 'end_bold'
    elif len(l.strip()) > 0:
      # This wasn't a quote - end conversation here
      if len(found) > 0:
        conversations.append(found)
        found = []
  elif mode == 'end_bold':
    if '</b>' not in l:
      bolded += ' ' + l
    else:
      bolded += ' ' + l.split('</b>')[0]
      bolded = wash_quote(bolded)
      if len(bolded) == 0 or '<b>' in l.split('</b>')[1]:
        mode = 'find_bold'
        i -= 1
      elif space_type in l:
        quote = l.split(space_type)[1]
        mode = 'find_quote'
      else:
        mode = 'find_bold'
  elif mode == 'find_quote':
    if '<b>' in l:
      quote += l.split('<b>')[0];
      found.append((bolded,wash_quote(quote)))
      bolded, quote = '', ''
      mode = 'find_bold'
      i -= 1
      if len(found) > 0:
        conversations.append(found)
        found = []
    elif len(l.strip()) > 0 and smaller_space_type in l[:len(smaller_space_type)]:
      quote += l
    else:
      found.append((bolded,wash_quote(quote)))
      bolded, quote = '', ''
      mode = 'find_bold' 
  i += 1

# Cleanup
if len(quote) > 0 and len(bolded) > 0:
  found.append((bolded,wash_quote(quote)))
if len(found) > 0:
  conversations.append(found)
  found = []

# print bolded, quote

with open('../data/scripts/%s.txt' % NAME, 'w') as f:
  for quotes in conversations:
    f.write("\n---\n\n")
    for actor,quote in quotes:
      f.write(actor + ":\n" + quote + "\n")

pickle.dump(conversations, open('../data/scripts/%s.pickle' % NAME, 'w'))