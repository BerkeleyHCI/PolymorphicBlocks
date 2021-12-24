# Simple tool that scans for libraries and dumps the whole thing to a proto file
# from typing import cast

# import edgir
# from edg_core.HdlInterfaceServer import LibraryElementResolver
# import edg_core
import edg
from edg.BoardCompiler import dump_library


if __name__ == '__main__':

  dump_library(edg, target_name = 'library', print_log = True)
