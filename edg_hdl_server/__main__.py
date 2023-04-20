from .Server import run_server


# In some cases stdout seems to buffer excessively, in which case starting python with -u seems to work
# https://stackoverflow.com/a/35467658/5875811
if __name__ == '__main__':
  run_server()
