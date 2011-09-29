import pickle, os.path

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