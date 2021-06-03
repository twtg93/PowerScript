import PowerScriptast as ast
import PowerScriptobjects as objs
import PowerScripttokenizer as tokenizer
import PowerScriptparser as parser

def bool_not(env, _, args):
  arg = args[0]
  bool_val = objs.make_bool(arg).val
  return objs.bool_from_py_bool(not bool_val)

UNARY_OPS = {
  "NOT": objs.not_,
  "SUB": objs.neg,
  "BOOLNOT": bool_not,
}

POW = {"POW"}
MUL_DIV = {"MUL", "DIV"}
ADD_SUB = {"ADD", "SUB"}
SHIFT = {"LSHIFT", "RSHIFT"}
BIN = {"AND", "OR", "XOR"}

SHORT_CIRCUITING = {"BOOLAND", "BOOLOR"}

BIN_OPS = {
  "POW": objs.pow_,
  "MUL": objs.mul,
  "DIV": objs.div,
  "ADD": objs.add,
  "SUB": objs.sub,
  "LSHIFT": objs.lshift,
  "RSHIFT": objs.rshift,
  "AND": objs.and_,
  "OR": objs.or_,
  "XOR": objs.xor,
}

CMP_OPS = {
  "EQ": objs.eq,
  "NEQ": objs.neq,
  "LEQ": objs.leq,
  "GEQ": objs.geq,
  "LT": objs.lt,
  "GT": objs.gt,
  "CONTAINS": objs.contains,
  "CONTAINED": objs.contained,
}

def eval_expr(env, expr):
  if isinstance(expr, ast.UnaryExpr):
    val = eval_expr(env, expr.val)
    return UNARY_OPS[expr.op](val, env, [val])

  elif isinstance(expr, ast.BinExpr):
    if expr.op in SHORT_CIRCUITING:
      if expr.op == "BOOLAND":
        left = eval_expr(env, expr.left)
        if objs.make_bool(left).val:
          return eval_expr(env, expr.right)
        else:
          return left

      elif expr.op == "BOOLOR":
        left = eval_expr(env, expr.left)
        if objs.make_bool(left).val:
          return left
        else:
          return eval_expr(env, expr.right)

    else:
      left = eval_expr(env, expr.left)
      right = eval_expr(env, expr.right)
      return BIN_OPS[expr.op](left, env, [left, right])

  elif isinstance(expr, ast.CmpExpr):
    vals = [eval_expr(env, val) for val in expr.vals]
    for op, lval, rval in zip(expr.ops, vals, vals[1:]):
      op = CMP_OPS[op]
      res = op(lval, env, [lval, rval])
      if not objs.make_bool(res).val:
        return objs.bool_from_py_bool(False)
    return objs.bool_from_py_bool(True)
  
  elif isinstance(expr, ast.DotExpr):
    val = eval_expr(env, expr.val)
    if expr.name in val.attrs:
      res = val.attrs[expr.name]
    elif expr.name in val.obj_type.attrs:
      res = val.obj_type.attrs[expr.name]
    else:
      raise objs.PowerScriptError(f"Can't find attribute {expr.name}")
      
    return res

  elif isinstance(expr, ast.CallExpr):
    args = [eval_expr(env, arg) for arg in expr.args]
    func = eval_expr(env, expr.func)
    return objs.call(func, env, [func] + args)
  
  elif isinstance(expr, ast.ColonCallExpr):
    expr_val = eval_expr(env, expr.expr)

    if expr.name in expr_val.attrs:
      func = expr_val.attrs[expr.name]
    elif expr.name in expr_val.obj_type.attrs:
      func = expr_val.obj_type.attrs[expr.name]
    else:
      raise obs.PowerScriptError(f"Can't find attribute {expr.name}")

    args = [eval_expr(env, arg) for arg in expr.args]
    return objs.call(func, env, [func, expr_val] + args)
  
  elif isinstance(expr, ast.IdentExpr):
    return env.get_var(expr.ident)
  
  elif isinstance(expr, ast.ListExpr):
    elems = [eval_expr(env, elem) for elem in expr.vals]
    return objs.list_from_py_list(elems)
  
  elif isinstance(expr, ast.NumLit):
    return objs.num_from_py_num(expr.val)
  
  elif isinstance(expr, ast.BoolLit):
    return objs.bool_from_py_bool(expr.val)
  
  elif isinstance(expr, ast.StrLit):
    return objs.string_from_py_string(expr.val)
  
  else:
    raise TypeError(f"Unknown expr type {type(expr)}")

def exec_line(env, line):
  if isinstance(line, ast.ExprLine):
    eval_expr(env, line.expr)
    
  elif isinstance(line, ast.SetLine):
    env.set_var(line.name, eval_expr(env, line.expr))

  elif isinstance(line, ast.IfLine):
    for cond, stmt in line.cond_codes:
      if objs.make_bool(eval_expr(env, cond)).val:
        exec_line(env, stmt)
        break
  
  elif isinstance(line, ast.WhileLine):
    while objs.make_bool(eval_expr(env, line.cond)).val:
      exec_line(env, line.line)
  
  elif isinstance(line, ast.FuncLine):
    func = objs.make_func(line.arg_names,
                          env.stack[-1],
                          line.line)
    env.set_var(line.name, func)
  
  elif isinstance(line, ast.ReturnLine):
    res = eval_expr(env, line.val)
    env.ret_stack[-1] = res

  elif isinstance(line, ast.Suite):
    exec_suite(env, line.lines)
  
  else:
    raise TypeError(f"Unknown line type {type(line)}")

def exec_suite(env, lines):
  for line in lines:
    exec_line(env, line)

def run_code(env, code):
  env.add_scopes([{}])
  toks = tokenizer.TokenStream(code)
  lines = parser.parse(toks)
  exec_suite(env, lines)
  env.remove_scope()

__all__ = ["run_code"]