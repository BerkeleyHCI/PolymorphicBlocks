from edg_hdl_server import __main__ as hdl_server


# If running the server locally, this is a wrapper around edg_hdl_server, which performs top-level imports
# that aren't available inside its directory
if __name__ == '__main__':
  hdl_server.run_server()
