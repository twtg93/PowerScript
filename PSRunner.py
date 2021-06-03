from PowerScriptexec import run_code
from PowerScriptenv import Env

# Read & Open PowerScript files.

with open("examples/name.ps") as f:
  code = f.read()
  
env = Env()
run_code(env, code)
