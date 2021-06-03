import collections

BOOL = {"BOOLAND", "BOOLOR", "BOOLNOT"}
POW = {"POW"}
MUL_DIV = {"MUL", "DIV"}
ADD_SUB = {"ADD", "SUB"}
SHIFT = {"LSHIFT", "RSHIFT"}
BIN = {"AND", "OR", "XOR"}
CMP = {"EQ", "NEQ", "LEQ", "GEQ", "LT",
       "GT", "CONTAINS", "CONTAINED"}

NODES = {
  "UnaryExpr": "op val",
  "BinExpr": "op left right",
  "CmpExpr": "ops vals",
  "DotExpr": "val name",
  "CallExpr": "func args",
  "ColonCallExpr": "expr name args",
  "IdentExpr": "ident",
  "ListExpr": "vals",
  "NumLit": "val",
  "BoolLit": "val",
  "StrLit": "val",

  "ExprLine": "expr",
  "SetLine": "name expr",
  "IfLine": "cond_codes",
  "WhileLine": "cond line",
  "FuncLine": "name arg_names line",
  "ReturnLine": "val",
  "Suite": "lines",
}

for name, fields in NODES.items():
  globals()[name] = collections.namedtuple(name, fields)