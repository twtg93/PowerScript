from PowerScriptobjects import *

builtins = {}

def builtin(name_=None):
  def deco(func):
    old_func = func
    def wrap(env, inst, args):
      return old_func(env, inst, args[1:])
    func = wrap

    name = name_
    if name is None:
      name = func.__name__
    builtins[name] = BuiltinFunc(func)
  return deco

@builtin("print")
def _(env, _, args):
  args = [make_string(arg).val for arg in args]
  print("".join(args))

@builtin("input")
def _(env, _, args):
  args = [make_string(arg).val for arg in args]
  return string_from_py_string(input("".join(args)))

@builtin("num")
def _(env, _, args):
  return make_num(*args)

@builtin("bool")
def _(env, _, args):
  return make_bool(*args)

@builtin("string")
def _(env, _, args):
  return make_string(*args)