import matplotlib.pyplot as plt
import matplotlib

def colors(length):
  colors=[]
  c = matplotlib.cm.get_cmap('gist_rainbow')
  for i in range(length):
    colors.append(c(1.*i/length))
  return colors

# Plot y against log x (semi-log plot)
def plot_semilog(name, dict, xlabel='', ylabel='', title='', linetype='k'):
	plt.clf()
	if len(xlabel) > 0:
		plt.xlabel(xlabel)
	if len(ylabel) > 0:
		plt.ylabel(ylabel)
	if len(title) > 0:
		plt.title(title)
		
	dicty = zip(*sorted(dict.iteritems()))
	plt.semilogx(dicty[0], dicty[1], linetype)
	plt.savefig('../data/images/%s.eps' % name)
	
# Plot y against log x (semi-log plot)
def plot_multiline(name, dict_array, xlabel='', ylabel='', title='', linetypes=['b','r','g','k'], labels=[], xlog=None, ylim=None):
  plt.clf()
  if len(xlabel) > 0:
  	plt.xlabel(xlabel)
  if len(ylabel) > 0:
  	plt.ylabel(ylabel)
  if len(title) > 0:
  	plt.title(title)
  if xlog:
    plt.xscale('log', basex=xlog)
  if ylim:
    plt.ylim(ylim)
  for dicty, linetype, label in zip(dict_array, linetypes, labels): 
    dicty = zip(*sorted(dicty.iteritems()))
    plt.plot(dicty[0], dicty[1], linetype, label=label)
  plt.legend()
  plt.savefig('../data/images/%s.eps' % name)

# Plot log y against log x (log-log plot)
def plot_loglog(name, dict, xlabel='', ylabel='', title='', linetype='k'):
	plt.clf()
	if len(xlabel) > 0:
		plt.xlabel(xlabel)
	if len(ylabel) > 0:
		plt.ylabel(ylabel)
	if len(title) > 0:
		plt.title(title)

	dicty = zip(*sorted(dict.iteritems()))
	plt.loglog(dicty[0], dicty[1], linetype)
	plt.savefig('../data/images/%s.eps' % name)	
	
# Plot y against log x (semi-log plot)
def plot_log(name, dict, xlabel='', ylabel='', title='', linetype='k', log=2):
	plt.clf()
	if len(xlabel) > 0:
		plt.xlabel(xlabel)
	if len(ylabel) > 0:
		plt.ylabel(ylabel)
	if len(title) > 0:
		plt.title(title)
		
	dicty = zip(*sorted(dict.iteritems()))
	plt.xscale('log', basex=log)
	plt.plot(dicty[0], dicty[1], linetype)
	plt.savefig('../data/images/%s.eps' % name)