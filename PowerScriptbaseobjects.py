from util import is_int

class PowerScriptError(RuntimeError):
  pass

ERR_TYPES = [
  "CallError",
  "MathError",
  "CompareError",
  "CastError",
]

for type_name in ERR_TYPES:
  globals()[type_name] = type(type_name, (PowerScriptError,), {})

# Object instance = object
def make_spec_meth(name, var_name=None):
  if not var_name:
    var_name = name
  
  def spec_meth(inst, env, args):
    meth = getattr(inst.obj_type, name)
    return meth(env, inst, args)
  
  globals()[var_name] = spec_meth
  return spec_meth

SPEC_METHS = [
  "call",

  "add",
  "sub",
  "mul",
  "div",
  ("pow", "pow_"),
  "neg",

  "lshift",
  "rshift",
  "and_",
  "or_",
  "xor",
  "not_",

  "contains",
  ("rcontains", "contained"),

  "eq",
  "neq",
  "leq",
  "geq",
  "lt",
  "gt",

  ("num", "num_cast"),
  ("bool", "bool_cast"),
  ("string", "string_cast"),
]

for meth in SPEC_METHS:
  if isinstance(meth, tuple):
    make_spec_meth(*meth)
  else:
    make_spec_meth(meth)


class Object(): # the object type class
  def __init__(self, obj_type, **kwargs):
    self.obj_type = obj_type
    self.attrs = kwargs
  
  def special_meth(name, err_str, err_type, right=None):
    def meth(self, env, inst, args):
      if name and name in self.attrs:
        func = self.attrs[name]
        res = func.obj_type.call(env, func,
                                  args)

        if res is not PowerScript_notimpl:
          return res
      
      if right and right in args[1].obj_type.attrs:
        new_recv = args[1]
        new_args = [args[1], args[0]] + args[2:]
        func = new_recv.obj_type.attrs[right]
        res = func.obj_type.call(env, func,
                                 new_args)

        if res is not PowerScript_notimpl:
          return res

      raise err_type(err_str.format(args[0].obj_type.attrs))

    return meth
  
  add = special_meth("__add", "Can't add {} and {}",
                     MathError, "__add")
  sub = special_meth("__sub", "Can't sub {} and {}",
                     MathError,"__rsub")
  mul = special_meth("__mul", "Can't mul {} and {}",
                     MathError,"__mul")
  div = special_meth("__div", "Can't div {} and {}",
                     MathError,"__rdiv")
  mod = special_meth("__mod", "Can't mod {} and {}",
                     MathError,"__rmod")
  pow = special_meth("__pow", "Can't pow {} and {}",
                     MathError,"__rpow")
  neg = special_meth("__neg", "Can't -{}",
                      MathError)

  lshift = special_meth("__lshift", "Can't left shift {}",
                        MathError)
  rshift = special_meth("__lshift", "Can't right shift {}",
                        MathError)
  and_ = special_meth("__and", "Can't & {} and {}", "__and",
                      MathError)
  or_ = special_meth("__or", "Can't | {} and {}", "__or",
                     MathError)
  xor = special_meth("__xor", "Can't ^ {} and {}", "__xor",
                     MathError)
  not_ = special_meth("__not", "Can't ~{}",
                      MathError)

  contains = special_meth("__in", "Can't test {} for membership",
                           CompareError)
  rcontains = special_meth(None, "Can't test {} for membership",
                          CompareError, "__in")
  
  eq = special_meth("__eq", "Can't test {} == {}",
                    CompareError, "__eq")
  neq = special_meth("__neq", "Can't test {} != {}",
                      CompareError, "__neq")
  leq = special_meth("__leq", "Can't test {} <= {}",
                      CompareError, "__geq")
  geq = special_meth("__geq", "Can't test {} >= {}",
                      CompareError, "__leq")
  lt = special_meth("__lt", "Can't test {} < {}",
                    CompareError, "__gt")
  gt = special_meth("__gt", "Can't test {} > {}",
                    CompareError, "__lt")

  call = special_meth("__call", "Can't call {}", CallError)

  num = special_meth("__num", "Can't convert {} to num",
                     CastError)
  bool = special_meth("__bool", "Can't convert {} to bool",
                      CastError)
  string = special_meth("__string", "Can't convert {} to string",
                        CastError)

  del special_meth
  

class Type(Object): # the type type class
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
  
  def call(self, env, _, args):
    obj = call(self.attrs["__new"], env, args)
    call(self.attrs["__init"], env, [obj] + args)
    success.val = True
    return obj

PowerScript_type = Type(None) 
PowerScript_type.obj_type = PowerScript_type
PowerScript_object = Object(Type)

PowerScript_notimpl_type = Object(PowerScript_type)
PowerScript_notimpl = Object(PowerScript_notimpl_type)
PowerScript_none_type = Object(PowerScript_type)
PowerScript_none = Object(PowerScript_none_type)

class BuiltinFuncType(Object):
  def __init__(self, *args, **kwargs):
    def __new():
      raise PowerScriptError("Cannot make BuiltinFunc instance")

    def __init():
      return
    
    kwargs.update(
      {
        "__new": BuiltinFunc(__new),
        "__init": BuiltinFunc(__init),
      }
    )
    super().__init__(*args, **kwargs)
  
  def call(self, env, inst, args):
    res = inst.func(env, inst, args)
    return res

class BuiltinFunc(Object):
  def __init__(self, func, *args, **kwargs):
    self.func = func
    super().__init__(*args, PowerScript_builtin, **kwargs)
  
  def __repr__(self):
    return f"builtin-{self.func.__qualname__}"

PowerScript_builtin = None # bootstrap the type for __new and init
PowerScript_builtin = BuiltinFuncType(PowerScript_type)
PowerScript_builtin.attrs["__new"].obj_type = PowerScript_builtin
PowerScript_builtin.attrs["__init"].obj_type = PowerScript_builtin
# finish bootstrapping