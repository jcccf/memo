import matplotlib.pyplot as plt

def histogram_plot(filename, xs, bins=1, normed=1, color='b', label='hello', ylim=None, xlim=None, xlabel=None, ylabel=None, histtype='stepfilled'):
  plt.clf()
  plt.figure().set_size_inches(20,10)
  n, bins, patches = plt.hist(xs, bins, normed=normed, histtype=histtype, rwidth=0.8, color=color, label=label)
  if xlabel:
    plt.xlabel(xlabel)
  if ylabel:
    plt.ylabel(ylabel)
  if ylim:
    plt.ylim(ylim)
  if xlim:
    plt.xlim(xlim)
  plt.legend()
  plt.savefig('%s' % filename)
  return (n, bins, patches)