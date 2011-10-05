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
  
def glob_filenames(directory='../../data/scripts/*.pickle'):
  return [os.path.split(f)[1] for f in glob.glob(directory)]

def print_scriptnames(filename='../../data/scripts/names.txt'):
  scriptnames = [x.split('.')[0] for x in glob_filenames()]
  with open(filename, 'w') as f:
    for s in scriptnames:
      f.write('%s\t\t%s\n' % (s, s.replace('_',' ')))
      
#print_scriptnames()