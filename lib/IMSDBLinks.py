from lxml.html import parse
import re, time, random, urllib, urllib2

  # L = 'http://www.imsdb.com/Movie%20Scripts/A%20Few%20Good%20Men%20Script.html'
  # 
  # Do query
  # ener = urllib2.build_opener()
  # y:
  # fil = opener.open(URL)
  # cept urllib2.HTTPError as detail:
  # print "Caught Error: ", detail
  # 
  # ot = parse(fil).getroot()
  # ot.make_links_absolute("http://www.imsdb.com/Movie%20Scripts/")
  # nks = root.cssselect(".script-details table a")
  # r l in links:
  # if "read" in l.text_content().lower():
  #   print l.attrib['href']
  
links, titles = [], []
    
for i in range(0,26):
  URL = 'http://www.imsdb.com/alphabetical/%s' % chr(ord('A')+i)
  lc = chr(ord('a')+i)
  
  opener = urllib2.build_opener()
  try:
    fil2 = opener.open(URL)
  except urllib2.HTTPError as detail:
    print "Caught Error: ", detail
    
  root = parse(fil2).getroot()
  root.make_links_absolute("http://www.imsdb.com/")
  for (e,a,link,_) in root.iterlinks():
    if "scripts" in link.lower() and a == 'href' and e.attrib.has_key('title') and e.attrib['title'].strip().lower()[0] == lc:
      # print e.attrib['href']
      links.append(link)
      title = e.attrib['title']
      if title[-6:] == 'Script':
        title = title[:-7].strip()
      titles.append(title)
  
# print titles

with open('../data/imsdb_titles.txt','w') as f:
  for t in titles:
    f.write(t+'\n')

raise Exception("Done")

script_links = []
for l in links:
  sleep_time = 0.5 * random.random()
  print "Sleeping for %f..." % sleep_time
  time.sleep(sleep_time)
  # print l
  # Do query
  opener = urllib2.build_opener()
  try:
    fil = opener.open(l.replace(' ','%20'))
  except urllib2.HTTPError as detail:
    print "Caught Error: ", detail
    
  root = parse(fil).getroot()
  root.make_links_absolute("http://www.imsdb.com/Movie%20Scripts/")
  tlinks = root.cssselect(".script-details table a")
  for t in tlinks:
    if "read" in t.text_content().lower():
      script_link = t.attrib['href']
      break
  script_links.append(script_link)

with open('../data/imsdb/a.txt', 'w') as f:
  for link in script_links:
    f.write(link+"\n")