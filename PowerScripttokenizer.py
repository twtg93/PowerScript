import re
import collections
import contextlib

TOKENS = [
  # keywords:
  ("BOOLAND", r"(and)(?:\W|$)", 1),
  ("BOOLOR", r"(or)(?:\W|$)", 1),
  ("BOOLNOT", r"(not)(?:\W|$)", 1),
  ("IF", r"(if)(?:\W|$)", 1),
  ("ELSE", r"(else)(?:\W|$)", 1),
  ("WHILE", r"(while)(?:\W|$)", 1),
  ("FUNC", r"(func)(?:\W|$)", 1),
  ("RETURN", r"(return)(?:\W|$)", 1),
  ("BOOL", r"(true|false)(?:\W|$)", 1),

  # other:
  ("COMMA", r","),
  ("DOT", r"\."),
  ("COLON", r":"),

  ("CONTAINED", r"<\|"),
  ("CONTAINS", r"\|>"),
  ("EQ", r"=="),
  ("NEQ", r"!="),
  ("LEQ", r"<="),
  ("GEQ", r">="),
  ("LT", r"<"),
  ("GT", r">"),

  ("POW", r"\*\*"),
  ("ADD", r"\+",),
  ("SUB", r"-"),
  ("MUL", r"\*"),
  ("DIV", r"/"),

  ("LSHIFT", r"<<"),
  ("RSHIFT", r">>"),
  ("AND", r"&"),
  ("OR", r"\|"),
  ("XOR", r"\^"),
  ("NOT", r"~"),

  ("EQUAL", r"="),

  ("NUM", r"[0-9]+(?:\.[0-9]*)?"),
  ("STRING", r'"(?:[^"\n]|\\["nt])*"'),
  ("IDENT", r"[a-zA-Z_][a-zA-Z_0-9]*"),

  ("OPAREN", r"\("),
  ("CPAREN", r"\)"),
  ("OBLOCK", r"{"),
  ("CBLOCK", r"}"),
  ("OLIST", r"\["),
  ("CLIST", r"\]"),

  # special:
  ("NEWLINE", r"\n"),
]  # lists are guaranteed ordered, but dicts arent in 3.6

MATCH_PRIORITY = {name: ind for ind, (name, *_)
                  in enumerate(TOKENS)}

KEYWORDS = {
  "BOOLAND",
  "BOOLOR",
  "BOOLNOT",
  "IF",
  "ELSE",
  "FUNC",
}

TOKENS = [
  (name, re.compile(val), *group)
  for name, val, *group in TOKENS
]

WHITESPACE = re.compile("[ \t\f]+")

Token = collections.namedtuple("Token", "name text ind")

class TokenStream():
  def __init__(self, code):
    self._ignore = collections.Counter()
    self.code = code
    self.tokens = list(_tokenize(code))
    self.ind = -1
    self.tok = None
    self.advance()
  
  def ignore(self, name):
    self._ignore[name] += 1
  
  def unignore(self, name):
    self._ignore[name] -= 1
  
  @contextlib.contextmanager
  def ignorectx(self, name):
    self.ignore(name)
    yield
    self.unignore(name)
  
  def ignored(self, name):
    return bool(self._ignore[name])
  
  def _advance(self):
    tok = self.tok
    self.ind += 1
    try:
      self.tok = self.tokens[self.ind]
    except IndexError:
      self.tok = Token("EOF", "", -1)
    return tok
  
  def advance(self):
    res = self._advance()
    while self.ignored(self.tok.name):
      res = self._advance()
    return res
  
  def copy(self):
    ts = object.__new__(TokenStream)
    ts.code = self.code
    ts.tokens = self.tokens
    ts.ind = self.ind
    ts.tok = self.tok
    ts._ignore = self._ignore.copy()
    return ts
  
  def replace_with(self, ts):
    self.tokens = ts.tokens
    self.ind = ts.ind
    self.tok = ts.tok
    self._ignore = ts._ignore

def _tokenize(code):
  curr_ind = 0
  while curr_ind < len(code):
    matches = set()
    for name, regex, *group in TOKENS:
      if group:
        group = group[0]
      else:
        group = 0
      
      match = regex.match(code, pos=curr_ind)
      if match:
        matches.add((name, match, group))

    if matches:
      if KEYWORDS & matches:
        return (KEYWORDS & matches).pop() # no keyword conflicts
      else:
        # select longest token; maximum munch rule
        def match_len(match):
          return (
            len(match[1].group(match[2])),
            -MATCH_PRIORITY[match[0]]
          )
        name, match, group = max(matches, key=match_len)
        
        curr_ind = match.end(group)
        yield Token(name=name, text=match.group(group), ind=curr_ind)

    else:
      match = WHITESPACE.match(code, pos=curr_ind)
      if match:
        curr_ind = match.end()
      else:
        err = (f"Unexpected char at index {curr_ind}: "
               f"{code[curr_ind]!r}")
        raise SyntaxError(err)