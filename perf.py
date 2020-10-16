import cProfile, pstats, io
from pstats import SortKey

from examples.test_datalogger import *

if __name__ == '__main__':

  ElectronicsDriver()  # pre-generate libs

  pr = cProfile.Profile()
  pr.enable()
  ElectronicsDriver().generate_write_block(TestDatalogger(), 'examples/test_datalogger')
  pr.disable()

  s = io.StringIO()
  sortby = SortKey.CUMULATIVE
  ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
  ps.print_stats()
  print(s.getvalue())
