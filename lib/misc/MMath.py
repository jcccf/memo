from math import *

def f(number, sigfig):
  return ("%.15f" % (round(number, int(-1 * floor(log10(number)) + (sigfig - 1))))).rstrip("0").rstrip(".")