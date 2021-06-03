import PowerScripttokenizer as tokenizer
import PowerScriptast as ast

# precedence:
# call: ()
# dot: .
# unary: - ~ not
# bool: and or
# e: **
# md: * / %
# as: + -
# shift: << >>
# bin: & | ^
# contains: <| |>
# cmp: == != <= >= < >

ESCAPES = {
  "n": "\n",
  "t": "\t",
}

UNARY = {"SUB", "NOT", "BOOLNOT"}
BOOL = {"BOOLAND", "BOOLOR"}
POW = {"POW"}
MUL_DIV = {"MUL", "DIV", "MOD"}
ADD_SUB = {"ADD", "SUB"}
SHIFT = {"LSHIFT", "RSHIFT"}
BIN = {"AND", "OR", "XOR"}
CMP = {"EQ", "NEQ", "LEQ", "GEQ", "LT",
       "GT", "CONTAINS", "CONTAINED"}

OPS = BOOL | POW | MUL_DIV | ADD_SUB | SHIFT | BIN | CMP

def get_line_pos(text, ind):
  before_ind = text[:ind]
  line = before_ind.count("\n") + 1
  pos = len(before_ind.rsplit("\n", 1)[1])
  return line, pos

def expected_err(toks, *types):
  if len(types) == 1:
    lst = types[0]
  elif len(types) == 2:
    lst = f"{types[0]} or {types[1]}"
  else:
    lst = ", ".join(types[:-1]) + ", or" + types[-1]
  code = toks.code
  line_no, pos = get_line_pos(code, toks.tok.ind)
  line = code.split("\n")[line_no - 1]
  marker = " " * pos + "^"
  raise SyntaxError(f"Expected {lst}, got {toks.tok.name}"
                    f" at line {line_no}:\n"
                    f"{line}\n{marker}")

# EXPRESSIONS

def parse_cmp(toks):
  sub_exprs = [parse_bin(toks)]
  ops = []
  while toks.tok.name in CMP:
    ops.append(toks.advance().name)
    sub_exprs.append(parse_bin(toks))
  
  if ops:
    return ast.CmpExpr(ops, sub_exprs)
  else:
    return sub_exprs[0]

parse_expr = parse_cmp

def parse_bin(toks):
  left = parse_shift(toks)
  if toks.tok.name in BIN:
    op = toks.advance().name
    right = parse_bin(toks)
    return ast.BinExpr(op, left, right)
  else:
    return left

def parse_shift(toks):
  left = parse_add_sub(toks)
  if toks.tok.name in SHIFT:
    op = toks.advance().name
    right = parse_shift(toks)
    return ast.BinExpr(op, left, right)
  else:
    return left

def parse_add_sub(toks):
  left = parse_mul_div(toks)
  if toks.tok.name in ADD_SUB:
    op = toks.advance().name
    right = parse_add_sub(toks)
    return ast.BinExpr(op, left, right)
  else:
    return left

def parse_mul_div(toks):
  left = parse_pow(toks)
  if toks.tok.name in MUL_DIV:
    op = toks.advance().name
    right = parse_mul_div(toks)
    return ast.BinExpr(op, left, right)
  else:
    return left

def parse_pow(toks):
  left = parse_bool(toks)
  if toks.tok.name in POW:
    op = toks.advance().name
    right = parse_pow(toks)
    return ast.BinExpr(op, left, right)
  else:
    return left

def parse_bool(toks):
  left = parse_unary(toks)
  if toks.tok.name in BOOL:
    op = toks.advance().name
    right = parse_bool(toks)
    return ast.BinExpr(op, left, right)
  return left

def parse_unary(toks):
  if toks.tok.name in UNARY:
    op = toks.advance().name
    return ast.UnaryExpr(op, parse_call(toks))
  else:
    return parse_call(toks)

def parse_call(toks):
  func = parse_colon(toks)
  if toks.tok.name == "OPAREN":
    return ast.CallExpr(func, parse_arglist(toks))
  else:
    return func

def parse_colon(toks):
  expr = parse_dotted(toks)
  while toks.tok.name == "COLON":
    toks.advance()
    if toks.tok.name == "IDENT":
      name = toks.advance().text
      if toks.tok.name == "OPAREN":
        args = parse_arglist(toks)
        return ast.ColonCallExpr(expr, name, args)
      else:
        expected_err(toks, "OPAREN")
    else:
      expected_err(toks, "IDENT")
  return expr

def parse_dotted(toks):
  expr = parse_base_expr(toks)
  if toks.tok.name == "DOT":
    toks.advance()
    if toks.tok.name == "IDENT":
      name = toks.advance().text
      return ast.DotExpr(expr, name)
    else:
      expected_err(toks, "IDENT")

  return expr

def parse_arglist(toks):
  args = []

  toks.advance()
  while toks.tok.name != "CPAREN":
    args.append(parse_expr(toks))

    if toks.tok.name == "COMMA":
      toks.advance()
    elif toks.tok.name == "CPAREN":
      break
    else:
      expected_err(toks, "COMMA", "CPAREN")
  
  toks.advance()

  return args

def parse_base_expr(toks):
  if toks.tok.name == "OPAREN":
    with toks.ignorectx("NEWLINE"):
      toks.advance()
      res = parse_expr(toks)
      if toks.tok.name != "CPAREN":
        expected_err(toks, "CPAREN")
      toks.advance()
      return res
  elif toks.tok.name == "IDENT":
    return ast.IdentExpr(toks.advance().text)
  else:
    return parse_literal(toks)

def parse_literal(toks):
  if toks.tok.name == "NUM":
    return parse_num_lit(toks)
  elif toks.tok.name == "BOOL":
    return parse_bool_lit(toks)
  elif toks.tok.name == "STRING":
    return parse_string_lit(toks)
  elif toks.tok.name == "OLIST":
    return parse_list(toks)
  else:
    expected_err(toks, "NUM", "OLIST")

def parse_num_lit(toks):
  text = toks.advance().text
  try:
    val = int(text)
  except:
    val = float(text)
  return ast.NumLit(val)

def parse_bool_lit(toks):
  return ast.BoolLit(toks.advance().text == "true")

def parse_string_lit(toks):
  res = ""
  text = toks.advance().text[1:-1]
  ind = 0
  while ind < len(text):
    if text[ind] == "\\":
      ind += 1
      res += ESCAPES.get(text[ind], text[ind])
    else:
      res += text[ind]
    ind += 1
  return ast.StrLit(res)

def parse_list(toks):
  res = []
  toks.advance()
  while toks.tok.name != "CLIST":
    res.append(parse_expr(toks))

    if toks.tok.name == "COMMA":
      toks.advance()
    elif toks.tok.name == "CLIST":
      break
    else:
      expected_err(toks, "COMMA", "CLIST")
  
  toks.advance()
  return ast.ListExpr(res)

# END EXPRESSIONS

def parse_line(toks):
  if toks.tok.name == "OBLOCK":
    toks.advance()
    lines = []
    while toks.tok.name != "CBLOCK":
      if toks.tok.name == "NEWLINE":
        toks.advance()
        continue
      
      lines.append(parse_line(toks))
      if toks.tok.name == "NEWLINE":
        toks.advance()
        continue
      elif toks.tok.name == "CBLOCK":
        break
      else:
        expected_err(toks, "NEWLINE", "CBLOCK")
    toks.advance()
    return ast.Suite(lines)

  elif toks.tok.name == "IF":
    return parse_if_clause(toks)
  
  elif toks.tok.name == "WHILE":
    return parse_while_clause(toks)
  
  elif toks.tok.name == "FUNC":
    return parse_func_def(toks)
  
  elif toks.tok.name == "RETURN":
    toks.advance()
    return ast.ReturnLine(parse_expr(toks))
  
  toks_copy = toks.copy()
  try:
    assignment = parse_assign(toks_copy)
  except SyntaxError:
    return ast.ExprLine(parse_expr(toks))
  else:
    toks.replace_with(toks_copy)
    return assignment

def parse_if_clause(toks):
  clauses = []
  while toks.tok.name == "IF":
    toks.advance()
    cond = parse_expr(toks)
    stmt = parse_line(toks)
    clauses.append((cond, stmt))
    if toks.tok.name == "EOF":
      return ast.IfLine(clauses)
    elif toks.tok.name == "NEWLINE":
      toks.advance()
    else:
      expected_err(toks, "NEWLINE", "EOF")
    
    if toks.tok.name == "ELSE":
      toks.advance()
    else:
      return ast.IfLine(clauses)
  cond = ast.BoolLit(val=True)
  stmt = parse_line(toks)
  clauses.append((cond, stmt))
  if toks.tok.name in {"NEWLINE", "EOF"}:
    toks.advance()
  else:
    expected_err(toks, "NEWLINE", "EOF")
  
  return ast.IfLine(clauses)

def parse_while_clause(toks):
  toks.advance()

  cond = parse_expr(toks)
  stmt = parse_line(toks)
  if toks.tok.name in {"NEWLINE", "EOF"}:
    return ast.WhileLine(cond, stmt)
  else:
    expected_err(toks, "NEWLINE", "EOF")

def parse_func_def(toks):
  toks.advance()

  if toks.tok.name == "IDENT":
    name = toks.advance().text
  else:
    expected_err(toks, "IDENT")

  if toks.tok.name != "OPAREN":
    expected_err(toks, "OPAREN")
    toks.advance()
  
  arg_names = []

  toks.advance()
  while toks.tok.name != "CPAREN":
    if toks.tok.name == "IDENT":
      arg_names.append(toks.advance().text)
    else:
      expected_err(toks, "IDENT")

    if toks.tok.name == "COMMA":
      toks.advance()
    elif toks.tok.name == "CPAREN":
      break
    else:
      expected_err(toks, "COMMA", "CPAREN")
  
  toks.advance()

  line = parse_line(toks)

  if toks.tok.name in {"NEWLINE", "EOF"}:
    return ast.FuncLine(name, arg_names, line)
  else:
    expected_err(toks, "NEWLINE", "EOF")
  
def parse_assign(toks):
  op = None
  if toks.tok.name == "IDENT":
    name = toks.advance().text
    if toks.tok.name in OPS:
      op = toks.advance().name
    
    if toks.tok.name == "EQUAL":
      toks.advance()
      expr = parse_expr(toks)
      if op:
        expr = ast.BinExpr(op, ast.IdentExpr(name), expr)
      return ast.SetLine(name, expr)
    else:
      expected_err(toks, "EQUAL")
  else:
    expected_err(toks, "IDENT")


def parse(toks):
  lines = []
  while toks.tok.name != "EOF":
    if toks.tok.name == "NEWLINE":
      toks.advance()
      continue

    lines.append(parse_line(toks))
    if toks.tok.name not in {"NEWLINE", "EOF"}:
      expected_err(toks, "NEWLINE", "EOF")
    toks.advance()
  return lines