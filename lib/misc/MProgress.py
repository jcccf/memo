import os.path, pickle

class Progress:
  def __init__(self, progress_filename):
    self.filename = progress_filename
    self.progress = {}
    if os.path.exists(progress_filename):
      self.progress = pickle.load(open(progress_filename, 'r'))

  def is_completed(self, attr1):
    if self.progress.has_key(attr1):
      return True
    else:
      return False
      
  def complete(self, attr1):
    if not self.progress.has_key(attr1):
      self.progress[attr1] = True

  def save(self):
    pickle.dump(self.progress, open(self.filename, 'w'))