from scikits.learn import svm, linear_model
import sqlite3, random
import nltk
 
# X = [[0, 0], [1, 1]]
# Y = [0, 1]
# clf = svm.SVC()
# print clf.fit(X, Y)

def load_examples(db_file):
  conn = sqlite3.connect(db_file)
  conn.text_factory = str
  c = conn.cursor()
  c.execute('SELECT q1.movie, q1.quote, q1.result, q2.result FROM quotes AS q1, quotes AS q2  WHERE q1.movie = q2.movie AND q1.quote = q2.quote AND q1.query_type=\'plain\' AND q2.query_type=\'movie_title\' AND q1.result > 0 AND q1.result > q2.result')
  return c.fetchall()
    
singles = load_examples('../data/db_quotes_parsed_single_sentences.sqlite')
negatis = load_examples('../data/db_negquotes_parsed_sentences.sqlite')

sx = [(r1,r2,r2/float(r1),r1-r2) for (_,_,r1,r2) in singles]
sy = [1] * len(sx)

nx = [(r1,r2,r2/float(r1),r1-r2) for (_,_,r1,r2) in negatis]
ny = [0] * len(nx)

  # nltk = [({'r1': r1,'r2': r2,'r21': r2/float(r1),'r1-2': r1-r2},1) for (_,_,r1,r2) in singles]
  # nltk = [({'r1': r1,'r2': r2,'r21': r2/float(r1),'r1-2': r1-r2},0) for (_,_,r1,r2) in singles]
  # ndom.shuffle(s_nltk)
  # ndom.shuffle(n_nltk)
  # nltk_train = s_nltk[:len(sx)/2]
  # nltk_test = s_nltk[len(sx)/2:]
  # nltk_train = n_nltk[:len(sx)/2]
  # nltk_test = n_nltk[len(sx)/2:]
  # nltk_test_d = [d for (d,_) in s_nltk_test]
  # nltk_test_y = [y for (_,y) in s_nltk_test]
  # nltk_test_d = [d for (d,_) in n_nltk_test]
  # nltk_test_y = [y for (_,y) in n_nltk_test]
  # assifier = nltk.WekaClassifier.train('../data/name.model',s_nltk_train+n_nltk_train, classifier='svm')
  # int classifier.labels()
  # edictions = classifier.batch_classify(s_nltk_test_d+n_nltk_test_d)
  # rrect = 0
  # r x,y in map(None, predictions, s_nltk_test_y+n_nltk_test_y):
  # if x == y:
  #   correct += 1
  # int correct, len(predictions), float(correct)/len(predictions)

random.shuffle(sx)
sx = sx[:len(nx)]
random.shuffle(nx)
sx_train = sx[:len(sx)/2]
sy_train = [1] * (len(sx)/2)
sx_test = sx[len(sx)/2:]
sy_test = [1] * (len(sx) - len(sx)/2)
nx_train = nx[:len(nx)/2]
ny_train = [0] * (len(nx)/2)
nx_test = nx[len(nx)/2:]
ny_test = [0] * (len(ny) - len(ny)/2)
print len(sx)
print len(nx)
clf = svm.SVC(probability=False)
print clf.fit(sx_train+nx_train, sy_train+ny_train)
predictions = clf.predict(sx_test+nx_test)
# print clf.predict_proba(sx_test+nx_test)
print clf.score(sx_test+nx_test, sy_test+ny_test)

correct = 0
for x,y in map(None, predictions, sy_test+ny_test):
  if x == y:
    correct += 1
print correct, len(predictions), float(correct)/len(predictions)

# clf = svm.SVC(kernel='linear')
# print clf.fit(sx+nx, sy+ny)
# print clf.coef_

# clf = linear_model.LinearRegression()
# print clf.fit(sx+nx, sy+ny)
# print clf.coef_