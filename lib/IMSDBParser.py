import re, time, random, urllib, urllib2, json
from QuoteFunctions import *

opener = urllib2.build_opener()
try:
  fil = opener.open('http://www.imsdb.com/scripts/A-Few-Good-Men.html')
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
found = []
while i < len(lines):
  l = lines[i]
  if mode == 'find_bold':
    if "<b>" in l:
      bolded = l.split('<b>')[1]
      mode = 'end_bold'
  elif mode == 'end_bold':
    if '</b>' not in l:
      bolded += ' ' + l
    else:
      bolded += ' ' + l.split('</b>')[0]
      bolded = whitespace_quote(bolded)
      if '                         ' in l:
        quote = l.split('                         ')[1]
        mode = 'find_quote'
      else:
        mode = 'find_bold'
  elif mode == 'find_quote':
    if len(l.strip()) > 0:
      quote += l
    else:
      quote = whitespace_quote(quote)
      found.append((bolded,quote))
      mode = 'find_bold' 
  i += 1
  if i == 300:
    break
    
print bolded, quote
actionless = [(actor,remove_brackets(quote)) for (actor,quote) in found]
print found
print actionless