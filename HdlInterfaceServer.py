import edg_hdl_server


# If running the server locally, this is a wrapper around edg_hdl_server, which performs top-level imports
# that aren't available inside its directory
if __name__ == '__main__':
  edg_hdl_server.run_server()
