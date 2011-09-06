from lxml.html import parse
import re, time, random, urllib, urllib2

# Returns number of results and all titles/urls on that result page
# ex. get_google("\"may the force be with you\"", 100) for the 10th result page
# the number of results returned improves as you go to result pages > 1
def get_google(query_string, start=1):
  # Sleep for some time so we don't get throttled
  sleep_time = 3 * random.random()
  print "Sleeping for %f..." % sleep_time
  time.sleep(sleep_time)
  
  # Do query
  query = urllib.quote_plus(query_string)
  opener = urllib2.build_opener()
  opener.addheaders = [('User-agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.7; rv:6.0.1) Gecko/20100101 Firefox/6.0.1'), ('Accept-Language', 'en-us,en;q=0.5)')]
  
  try:
    fil = opener.open('http://www.google.com/search?q=%s&start=%d' % (query,start))
  except HTTPError as detail:
    print detail
    return None
  
  root = parse(fil).getroot()
  text_node = root.cssselect("#resultStats")
  
  if len(text_node) == 0:
    if "did not match any documents" in root.text_content():
      return (0, [])
    else:
      print root.text_content()
      return None

  text_node = text_node[0].text_content().encode('utf-8')
  
  top_urls = [(node.text_content().encode('utf-8'),node.get("href")) for node in root.cssselect("h3.r a")]
  
  matcher = re.compile("\w*Page ([0-9]+) of (about )*([0-9\,]+) results.*")
  
  #print text_node
  num_results = int(matcher.match(text_node).group(3).replace(",",""))
  
  return (num_results, top_urls)
  
print get_google("\"star wars\" \"may the force be with you\"", 100)