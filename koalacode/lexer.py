import re

TOKEN_SPEC = [
    ('NUMBER',   r'\d+'),
    ('STRING',   r'"[^"]*"'),
    ('ID',       r'[A-Za-z_][A-Za-z0-9_]*'),
    ('ASSIGN',   r'='),
    ('SEMI',     r';'),
    ('LPAREN',   r'\('),
    ('RPAREN',   r'\)'),
    ('LBRACE',   r'\{'),
    ('RBRACE',   r'\}'),
    ('LBRACK',   r'\['),
    ('RBRACK',   r'\]'),
    ('COMMA',    r','),
    ('OP',       r'==|!=|<=|>=|&&|\|\||[+\-*/<>!]'),
    ('COMMENT',  r'#.*'),
    ('SKIP',     r'[ \t\n]+'),
    ('MISMATCH', r'.'),
]

KEYWORDS = {"give", "take", "this", "otherwise", "iter", "iter2", "true", "false", "func", "return"}

class Token:
    def __init__(self, type_, value, line, col):
        self.type = type_
        self.value = value
        self.line = line
        self.col = col
    def __repr__(self):
        return f"Token({self.type},{self.value}, line={self.line}, col={self.col})"

def tokenize(code):
    code = code.replace("\r\n", "\n").replace("\r", "\n")
    tok_regex = '|'.join(f'(?P<{name}>{pattern})' for name, pattern in TOKEN_SPEC)
    line_num = 1
    line_start = 0
    tokens = []
    for mo in re.finditer(tok_regex, code):
        kind = mo.lastgroup
        value = mo.group()
        column = mo.start() - line_start + 1

        if kind == 'NUMBER':
            value = int(value)
        elif kind == 'STRING':
            value = value[1:-1]
        elif kind == 'ID' and value in KEYWORDS:
            kind = value.upper()
        elif kind == 'SKIP':
            if '\n' in value:
                line_num += value.count('\n')
                line_start = mo.end()
            continue
        elif kind == 'COMMENT':
            continue
        elif kind == 'MISMATCH':
            raise RuntimeError(f"[Line {line_num}, Col {column}] Unexpected token: {value}")

        tokens.append(Token(kind, value, line_num, column))
    tokens.append(Token('EOF', None, line_num, column))
    return tokens
