import pickle, os.path, os, glob

def pickle_load_mac(filename):
  mac_file = filename+".mac"
  
  # Code to convert from windows to mac file since pickle complains
  if not os.path.exists(mac_file):
    print "Generating Mac version of file..."
    file = open(filename,'r')
    movies = file.read().replace('\r\n','\n')
    f = open(mac_file,'w')
    f.write(movies)
    f.close()

  return pickle.load(open(mac_file,'r'))
  
# Get a list of files in a directory
def glob_filenames(directory='../../data/scripts/*.pickle'):
  return [os.path.split(f)[1] for f in glob.glob(directory)]

# Print out list of scriptnames in some directory
def print_scriptnames(filename='../../data/scripts/names.txt'):
  scriptnames = [x.split('.')[0] for x in glob_filenames()]
  with open(filename, 'w') as f:
    for s in scriptnames:
      f.write('%s\t\t%s\n' % (s, s.replace('_',' ')))

# For some file printed out by print_scriptnames, arrange the script titles so that "hello, the" becomes "the hello"
def prettyprint_scriptnames(ofilename='../../data/scripts/names_old.txt', nfilename='../../data/scripts/names_pretty.txt'):
  with open(ofilename, 'r') as f:
    with open(nfilename, 'w') as f2:
      for l in f:
        p1, p2 = l.replace('\n','').split('\t\t')
        if ', the' in p2:
          p2 = 'the ' + p2.replace(', the', '')
        if ', a' in p2:
          p2 = 'a ' + p2.replace(', a', '')
        f2.write('%s\t\t%s\n' % (p1, p2))
      
def generate_names_file_from_dict_keys(filename='../../data/pn2/negativelinesdict.newdata.pickle'):
  a = pickle.load(open(filename,'r'))
  with open(filename+'.txt', 'w') as f:
    for k in a.keys():
      f.write(k+'\t\t'+k+'\n')

# generate_names_file_from_dict_keys()
