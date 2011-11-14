from misc import *
import os.path, shutil

def output_thes(filename, filename_output, output_all=False):
  with open(filename_output, 'w') as f2:
    with open(filename, 'r') as f:
      for l in f:
        fn, om = l.replace('\n', '').split('\t\t')
        if ', the' in om or ', a' in om:
          f2.write("%s\t\t%s\n" % (fn, MQuote.clean_movie_title(om)))
        elif output_all:
          f2.write("%s\n\n")

# Copy Thes Into Another Directory
def copy_into_new_directory(directory, names_file):
  dir = directory+'/thes'
  if not os.path.exists(dir):
    os.makedirs(dir)
  with open(names_file, 'r') as f:
    for l in f:
      fn, om = l.replace('\n', '').split('\t\t')
      try:
        shutil.move(directory+'/'+fn+'.bing.sqlite', directory+'/thes/'+fn+'.bing.sqlite')
      except Exception as detail:
        print "Exception: ", detail
      
output_thes('../data/scripts/names.txt', '../data/scripts/names_thes.txt')
output_thes('../data/scripts/names_cham_unique_dedup.txt', '../data/scripts/names_cham_unique_dedup_thes.txt')
copy_into_new_directory('../data/scripts/db', '../data/scripts/names_thes.txt')
copy_into_new_directory('../data/scripts/db', '../data/scripts/names_cham_unique_dedup_thes.txt')