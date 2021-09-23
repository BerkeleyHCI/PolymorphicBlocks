import cProfile, pstats, io
from pstats import SortKey

from edg import compile_board_inplace
from examples.test_datalogger import TestDatalogger

if __name__ == '__main__':
  pr = cProfile.Profile()
  pr.enable()
  compile_board_inplace(TestDatalogger)
  pr.disable()

  s = io.StringIO()
  sortby = SortKey.CUMULATIVE
  ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
  ps.print_stats()
  print(s.getvalue())
