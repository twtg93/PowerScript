from PowerScriptobjects import PowerScriptError, PowerScript_none
from PowerScriptbuiltins import builtins

class Env():
  def __init__(self, builtins=builtins):
    self.stack = [[]]
    self.ret_stack = [None]
    self.builtins = builtins
  
  def find_in_frame(self, frame, name):
    for scope in reversed(frame):
      if name in scope:
        return scope
    raise NameError()

  def _get_dict(self, name):
    if name in self.builtins:
      return self.builtins
    
    try:
      return self.find_in_frame(self.stack[-1], name)
    except NameError:
      pass

    try:
      return self.find_in_frame(self.stack[0], name)
    except NameError:
      pass
    
    raise PowerScriptError(f"Variable {name} not found")
  
  def get_var(self, name):
    return self._get_dict(name)[name]
  
  def set_var(self, name, val):
    try:
      self._get_dict(name)[name] = val
    except PowerScriptError:
      self.stack[-1][-1][name] = val
  
  def add_frame(self, scopes):
    self.stack.append(list(scopes))
    self.ret_stack.append(PowerScript_none)
  
  def add_scopes(self, scopes):
    self.stack[-1].extend(scopes)
  
  def remove_scope(self, count=1):
    for _ in range(count):
      self.stack[-1].pop()
  
  def remove_frame(self):
    self.stack.pop()
    return self.ret_stack.pop()