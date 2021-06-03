from PowerScriptbaseobjects import *
import PowerScriptexec

def make_empty_obj(type_, **attrs):
  return Object(type_, **attrs)

def __new_num(env, _, args):
  return make_empty_obj(PowerScript_num)

def __init_num(env, _, args):
  obj, *args = args
  if len(args) == 0:
    obj.val = 0
  elif len(args) == 1:
    arg = args[0]
    obj.val = num_cast(arg, env, [arg]).val
  else:
    raise PowerScriptError("Too many arguments passed to num()")

def __add_num(env, _, args):
  assert len(args) == 2
  if args[1].obj_type is PowerScript_num:
    return num_from_py_num(args[0].val + args[1].val)
  else:
    return PowerScript_notimpl

def __sub_num(env, _, args):
  assert len(args) == 2
  if args[1].obj_type is PowerScript_num:
    return num_from_py_num(args[0].val - args[1].val)
  else:
    return PowerScript_notimpl

def __mul_num(env, _, args):
  assert len(args) == 2
  if args[1].obj_type is PowerScript_num:
    return num_from_py_num(args[0].val * args[1].val)
  else:
    return PowerScript_notimpl

def __div_num(env, _, args):
  assert len(args) == 2
  if args[1].obj_type is PowerScript_num:
    if args[1].val == 0:
      raise PowerScriptError("Division by 0")
    return num_from_py_num(args[0].val / args[1].val)
  else:
    return PowerScript_notimpl

def __mod_num(env, _, args):
  assert len(args) == 2
  if args[1].obj_type is PowerScript_num:
    if args[1].val == 0:
      raise PowerScriptError("Modulo by 0")
    return num_from_py_num(args[0].val / args[1].val)
  else:
    return PowerScript_notimpl

def __pow_num(env, _, args):
  assert len(args) == 2
  if args[1].obj_type is PowerScript_num:
    return num_from_py_num(args[0].val ** args[1].val)
  else:
    return PowerScript_notimpl

def __neg_num(env, _, args):
  assert len(args) == 1
  return num_from_py_num(-args[0].val)

def to_int(num):
  if is_int(num.val):
    return int(num.val)
  else:
    raise PowerScriptError(f"Cannot convert {num.val} to integer")

def shift(num, sh):
  if sh > 0:
    return num << sh
  else:
    return num >> -sh

def __lshift_num(env, _, args):
  assert len(args) == 2
  if args[1].obj_type is PowerScript_num:
    sh = to_int(args[1])
    return num_from_py_num(shift(args[0].val, sh))
  else:
    return PowerScript_notimpl

def __rshift_num(env, _, args):
  assert len(args) == 2
  if args[1].obj_type is PowerScript_num:
    sh = to_int(args[1])
    return num_from_py_num(shift(args[0].val, -sh))
  else:
    return PowerScript_notimpl

def __and_num(env, _, args):
  assert len(args) == 2

  if args[1].obj_type is PowerScript_num:
    a = to_int(args[0])
    b = to_int(args[1])
    return num_from_py_num(a & b)
  else:
    return PowerScript_notimpl

def __or_num(env, _, args):
  assert len(args) == 2

  if args[1].obj_type is PowerScript_num:
    a = to_int(args[0])
    b = to_int(args[1])
    return num_from_py_num(a | b)
  else:
    return PowerScript_notimpl

def __xor_num(env, _, args):
  assert len(args) == 2

  if args[1].obj_type is PowerScript_num:
    a = to_int(args[0])
    b = to_int(args[1])
    return num_from_py_num(a ^ b)
  else:
    return PowerScript_notimpl

def __not_num(env, _, args):
  assert len(args) == 1

  if args[1].obj_type is PowerScript_num:
    a = to_int(args[0])
    return num_from_py_num(~a)
  else:
    return PowerScript_notimpl

def __eq_num(env, _, args):
  assert len(args) == 2
  if args[1].obj_type is PowerScript_num:
    return bool_from_py_bool(args[0].val == args[1].val)
  else:
    return PowerScript_notimpl

def __neq_num(env, _, args):
  assert len(args) == 2
  if args[1].obj_type is PowerScript_num:
    return bool_from_py_bool(args[0].val != args[1].val)
  else:
    return PowerScript_notimpl

def __leq_num(env, _, args):
  assert len(args) == 2
  if args[1].obj_type is PowerScript_num:
    return bool_from_py_bool(args[0].val <= args[1].val)
  else:
    return PowerScript_notimpl

def __geq_num(env, _, args):
  assert len(args) == 2
  if args[1].obj_type is PowerScript_num:
    return bool_from_py_bool(args[0].val >= args[1].val)
  else:
    return PowerScript_notimpl

def __lt_num(env, _, args):
  assert len(args) == 2
  if args[1].obj_type is PowerScript_num:
    return bool_from_py_bool(args[0].val < args[1].val)
  else:
    return PowerScript_notimpl

def __gt_num(env, _, args):
  assert len(args) == 2
  if args[1].obj_type is PowerScript_num:
    return bool_from_py_bool(args[0].val > args[1].val)
  else:
    return PowerScript_notimpl

def __num_num(env, _, args):
  return num_from_py_num(args[0].val)

def __bool_num(env, _, args):
  return bool_from_py_bool(args[0].val)

def __string_num(env, _, args):
  val = args[0].val
  if is_int(val):
    val = int(val)
  return string_from_py_string(str(val))

def make_num(*args):
  args = list(args)
  obj = __new_num(None, None, args)
  __init_num(None, None, [obj] + args)
  return obj

def num_from_py_num(num):
  obj = __new_num(None, None, None)
  obj.val = num
  return obj

num_attrs = {
  "__new": BuiltinFunc(__new_num),
  "__init": BuiltinFunc(__init_num),
  "__add": BuiltinFunc(__add_num),
  "__sub": BuiltinFunc(__sub_num),
  "__mul": BuiltinFunc(__mul_num),
  "__div": BuiltinFunc(__div_num),
  "__mod": BuiltinFunc(__mod_num),
  "__pow": BuiltinFunc(__pow_num),
  "__neg": BuiltinFunc(__neg_num),

  "__lshift": BuiltinFunc(__lshift_num),
  "__rshift": BuiltinFunc(__rshift_num),
  "__and": BuiltinFunc(__and_num),
  "__or": BuiltinFunc(__or_num),
  "__xor": BuiltinFunc(__xor_num),
  "__not": BuiltinFunc(__not_num),

  "__eq": BuiltinFunc(__eq_num),
  "__neq": BuiltinFunc(__neq_num),
  "__leq": BuiltinFunc(__leq_num),
  "__geq": BuiltinFunc(__geq_num),
  "__lt": BuiltinFunc(__lt_num),
  "__gt": BuiltinFunc(__gt_num),

  "__num": BuiltinFunc(__num_num),
  "__bool": BuiltinFunc(__bool_num),
  "__string": BuiltinFunc(__string_num),
}

PowerScript_num = Object(PowerScript_type, **num_attrs)


def __new_bool(env, _, args):
  return make_empty_obj(PowerScript_bool)

def __init_bool(env, _, args):
  obj, *args = args
  if not args:
    obj.val = False
  elif len(args) == 1:
    arg = args[0]
    obj.val = bool_cast(arg, env, [arg]).val
  else:
    raise PowerScriptError("Too many arguments passed to bool")

def __bool_bool(env, _, args):
  return bool_from_py_bool(args[0].val)

def __string_bool(env, _, args):
  string = "true" if args[0].val else "false"
  return string_from_py_string(string)

def make_bool(*args):
  args = list(args)
  obj = __new_bool(None, None, args)
  __init_bool(None, None, [obj] + args)
  return obj

def bool_from_py_bool(bool_):
  obj = __new_bool(None, None, None)
  obj.val = bool(bool_)
  return obj


bool_attrs = {
  "__new": BuiltinFunc(__new_bool),
  "__init": BuiltinFunc(__init_bool),
  "__bool": BuiltinFunc(__bool_bool),
  "__string": BuiltinFunc(__string_bool),
}

PowerScript_bool = Object(PowerScript_type, **bool_attrs)

def __new_string(env, _, args):
  return make_empty_obj(PowerScript_string)

def __init_string(env, _, args):
  obj, *args = args
  str_args = [(string_cast(arg, env, [arg])).val
              for arg in args]
  obj.val = "".join(str_args)

def __add_string(env, _, args):
  assert len(args) == 2
  if args[1].obj_type is PowerScript_string:
    return string_from_py_string(args[0].val + args[1].val)
  else:
    return PowerScript_notimpl

def __mul_string(env, _, args):
  assert len(args) == 2
  if args[1].obj_type is PowerScript_num:
    mul = to_int(args[1])
    return string_from_py_string(args[0].val * mul)
  else:
    return PowerScript_notimpl

def __call_string(env, _, args):
  assert len(args) == 2
  if args[1].obj_type is PowerScript_num:
    ind = to_int(args[1])
    return string_from_py_string(args[0].val[ind])
  else:
    return PowerScript_notimpl

def __eq_string(env, _, args):
  assert len(args) == 2
  if args[1].obj_type is PowerScript_string:
    return bool_from_py_bool(args[0].val == args[1].val)
  else:
    return PowerScript_notimpl

def __neq_string(env, _, args):
  assert len(args) == 2
  if args[1].obj_type is PowerScript_string:
    return bool_from_py_bool(args[0].val != args[1].val)
  else:
    return PowerScript_notimpl

def __in_string(env, _, args):
  assert len(args) == 2
  if args[1].obj_type is PowerScript_string:
    return bool_from_py_bool(args[0].val in args[1].val)
  else:
    return PowerScript_notimpl

def __num_string(env, _, args):
  val = args[0].val
  try:
    val = int(val)
  except ValueError:
    try:
      val = float(val)
    except ValueError:
      raise PowerScriptError("Can't cast {val} to number")
  return num_from_py_num(val)

def __bool_string(env, _, args):
  return bool_from_py_bool(args[0].val)

def __string_string(env, _, args):
  return string_from_py_string(args[0].val)

def len_string(env, _, args):
  return num_from_py_num(len(args[1].val))

def string_from_py_string(string):  
  obj = __new_string(None, None, None)
  obj.val = string
  return obj

def make_string(*args):
  args = list(args)
  obj = __new_string(None, None, args)
  __init_string(None, None, [obj] + args)
  return obj

string_attrs = {
  "__new": BuiltinFunc(__new_string),
  "__init": BuiltinFunc(__init_string),
  "__add": BuiltinFunc(__add_string),
  "__mul": BuiltinFunc(__mul_string),
  "__call": BuiltinFunc(__call_string),
  
  "__eq": BuiltinFunc(__eq_string),
  "__neq": BuiltinFunc(__neq_string),

  "__in": BuiltinFunc(__in_string),

  "__num": BuiltinFunc(__num_string),
  "__bool": BuiltinFunc(__bool_string),
  "__string": BuiltinFunc(__string_string),

  "len": BuiltinFunc(len_string),
}

PowerScript_string = Object(PowerScript_type, **string_attrs)


def __new_list(env, _, args):
  return make_empty_obj(PowerScript_list)

def __init_list(env, _, args):
  obj, *args = args
  obj.vals = list(args)

def __add_list(env, _, args):
  assert len(args) == 2
  if args[1].obj_type is PowerScript_list:
    return list_from_py_list(args[0].vals + args[1].vals)
  else:
    return PowerScript_notimpl

def __call_list(env, _, args):
  assert len(args) == 2
  if args[1].obj_type is PowerScript_num:
    val = to_int(args[1])
    return args[0].vals[val]
  else:
    return PowerScript_notimpl

def __eq_list(env, _, args):
  assert len(args) == 2
  if args[1].obj_type is PowerScript_list:
    if len(args[0].vals) != len(args[1]).vals:
      return bool_from_py_bool(False)
    
    iter_ = zip(args[0].vals, args[1].vals,)
    equal = all(
      make_bool(eq(env, lval, [lval, rval])).val
      for lval, rval in iter_
    )
    return bool_from_py_bool(equal)
  else:
    return PowerScript_notimpl

def __neq_list(env, _, args):
  assert len(args) == 2
  if args[1].obj_type is PowerScript_list:
    if len(args[0].vals) != len(args[1]).vals:
      return bool_from_py_bool(True)
    
    iter_ = zip(args[0].vals, args[1].vals,)
    equal = all(
      make_bool(eq(env, lval, [lval, rval])).val
      for lval, rval in iter_
    )
    return bool_from_py_bool(not equal)
  else:
    return PowerScript_notimpl

def __in_list(env, _, args):
  assert len(args) == 2
  for elem in args[0].vals:
    if make_bool(eq(args[1], env, [args[1], elem])).val:
      return bool_from_py_bool(True)
  return bool_from_py_bool(False)

def len_list(env, _, args):
  return num_from_py_num(len(args[1].vals))

def append_list(env, _, args):
  args[1].vals.append(args[2])
  return PowerScript_none

def pop_list(env, _, args):
  if args[1].vals:
    return args[1].vals.pop()
  else:
    raise PowerScriptError("Pop from empty list")

def list_from_py_list(vals):
  obj = __new_list(None, None, None)
  obj.vals = vals
  return obj

def make_list(*args):
  obj = __new_list(None, None, args)
  __init_list(None, None, [obj] + args)
  return obj

list_attrs = {
  "__new": BuiltinFunc(__new_list),
  "__init": BuiltinFunc(__init_list),
  "__add": BuiltinFunc(__add_list),
  "__call": BuiltinFunc(__call_list),

  "__eq": BuiltinFunc(__eq_list),
  "__neq": BuiltinFunc(__neq_list),

  "__in": BuiltinFunc(__in_list),

  "len": BuiltinFunc(len_list),
  "append": BuiltinFunc(append_list),
  "pop": BuiltinFunc(pop_list),
}

PowerScript_list = Object(PowerScript_type, **list_attrs)


def __new_dict(env, _, args):
  return make_empty_obj(PowerScript_func)

dict_attrs = {

}

PowerScript_dict = Object(PowerScript_type, **dict_attrs)


def __new_func(env, _, args):
  return make_empty_obj(PowerScript_func)

def __init_func(env, _, args):
  raise PowerScriptError("Cannot init Func")

def __call_func(env, _, args):
  obj, *args = args
  env.add_frame(scope.copy() for scope in obj.scopes)
  env.add_scopes([dict(zip(obj.arg_names, args))])
  PowerScriptexec.exec_line(env, obj.line)
  return env.remove_frame()

def make_func(arg_names, scopes, line):
  obj = __new_func(None, None, None)
  obj.arg_names = arg_names
  obj.scopes = scopes
  obj.line = line
  return obj


func_attrs = {
  "__call": BuiltinFunc(__call_func),
  # TODO: finish dicts, add ast nodes
}

PowerScript_func = Object(PowerScript_type, **func_attrs)