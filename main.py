from PowerScriptexec import run_code
from PowerScriptenv import Env

# put code in code.ps

with open("code.ps") as f:
  code = f.read()

#print(tok(code).tokens)

env = Env()
run_code(env, code)