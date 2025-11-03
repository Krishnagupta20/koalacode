class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.cur = self.tokens[self.pos]

    def _advance(self):
        self.pos += 1
        self.cur = self.tokens[self.pos]

    def _eat(self, ttype):
        if self.cur.type == ttype:
            self._advance()
        else:
            raise RuntimeError(
                f"Expected {ttype} at line {self.cur.line}, col {self.cur.col}, got {self.cur.type}"
            )

    def parse(self):
        stmts = []
        while self.cur.type != 'EOF':
            stmts.append(self.statement())
        return ('block', stmts, self.cur.line, self.cur.col)


    def assignment(self):
        if self.cur.type == 'ID':
            name, line, col = self.cur.value, self.cur.line, self.cur.col
            self._advance()
            if self.cur.type == 'ASSIGN':
                self._advance()
                val = self.comparison()
                return ('assign', name, val, line, col)
        raise RuntimeError(f"Invalid assignment at line {self.cur.line}, col {self.cur.col}")

    def statement(self):
        if self.cur.type == 'FUNC':
            line, col = self.cur.line, self.cur.col
            self._advance()
            name = self.cur.value; self._eat('ID')
            self._eat('LPAREN')
            params = []
            if self.cur.type != 'RPAREN':
                params.append(self.cur.value); self._eat('ID')
                while self.cur.type == 'COMMA':
                    self._advance(); params.append(self.cur.value); self._eat('ID')
            self._eat('RPAREN')
            body = self.statement()
            return ('func_def', name, params, body, line, col)

        if self.cur.type == 'RETURN':
            line, col = self.cur.line, self.cur.col
            self._advance()
            val = self.comparison()
            self._eat('SEMI')
            return ('return', val, line, col)

        if self.cur.type == 'GIVE':
            line, col = self.cur.line, self.cur.col
            self._advance(); self._eat('LPAREN')
            expr = self.comparison()
            self._eat('RPAREN'); self._eat('SEMI')
            return ('give', expr, line, col)

        if self.cur.type == 'TAKE':
            line, col = self.cur.line, self.cur.col
            self._advance(); self._eat('LPAREN'); self._eat('RPAREN'); self._eat('SEMI')
            return ('take', line, col)

        if self.cur.type == 'THIS':
            line, col = self.cur.line, self.cur.col
            self._advance(); self._eat('LPAREN')
            cond = self.comparison()
            self._eat('RPAREN')
            then_branch = self.statement()
            else_branch = None
            if self.cur.type == 'OTHERWISE':
                self._advance(); else_branch = self.statement()
            return ('if', cond, then_branch, else_branch, line, col)

        if self.cur.type == 'ITER':
            line, col = self.cur.line, self.cur.col
            self._advance(); self._eat('LPAREN')
            cond = self.comparison()
            self._eat('RPAREN')
            body = self.statement()
            return ('while', cond, body, line, col)

        if self.cur.type == 'ITER2':
            line, col = self.cur.line, self.cur.col
            self._advance(); self._eat('LPAREN')
            init = self.assignment(); self._eat('SEMI')
            cond = self.comparison(); self._eat('SEMI')
            step = self.assignment(); self._eat('RPAREN')
            body = self.statement()
            return ('for', init, cond, step, body, line, col)

        if self.cur.type == 'LBRACE':
            line, col = self.cur.line, self.cur.col
            self._advance()
            stmts = []
            while self.cur.type != 'RBRACE':
                stmts.append(self.statement())
            self._eat('RBRACE')
            return ('block', stmts, line, col)

        if self.cur.type == 'ID':
            name, line, col = self.cur.value, self.cur.line, self.cur.col
            self._advance()
            if self.cur.type == 'ASSIGN':
                self._advance(); val = self.comparison(); self._eat('SEMI')
                return ('assign', name, val, line, col)
            elif self.cur.type == 'LBRACK':  # arr[idx] = val
                self._advance(); idx = self.comparison(); self._eat('RBRACK')
                self._eat('ASSIGN'); val = self.comparison(); self._eat('SEMI')
                return ('assign_index', name, idx, val, line, col)
            elif self.cur.type == 'LPAREN':  # func call
                self._advance(); args = []
                if self.cur.type != 'RPAREN':
                    args.append(self.comparison())
                    while self.cur.type == 'COMMA':
                        self._advance(); args.append(self.comparison())
                self._eat('RPAREN'); self._eat('SEMI')
                return ('func_call', name, args, line, col)
            else:
                self._eat('SEMI')
                return ('expr', ('var', name, line, col), line, col)

        line, col = self.cur.line, self.cur.col
        expr = self.comparison()
        self._eat('SEMI')
        return ('expr', expr, line, col)


    def comparison(self):
        node = self.expr()
        while self.cur.type == 'OP' and self.cur.value in ('<', '>', '<=', '>=', '==', '!=', '&&', '||'):
            op, line, col = self.cur.value, self.cur.line, self.cur.col
            self._advance()
            node = ('binop', op, node, self.expr(), line, col)
        return node

    def expr(self):
        node = self.term()
        while self.cur.type == 'OP' and self.cur.value in ('+', '-'):
            op, line, col = self.cur.value, self.cur.line, self.cur.col
            self._advance()
            node = ('binop', op, node, self.term(), line, col)
        return node

    def term(self):
        node = self.factor()
        while self.cur.type == 'OP' and self.cur.value in ('*', '/'):
            op, line, col = self.cur.value, self.cur.line, self.cur.col
            self._advance()
            node = ('binop', op, node, self.factor(), line, col)
        return node

    def factor(self):
        tok = self.cur
        if tok.type == 'NUMBER':
            self._advance(); return ('num', tok.value, tok.line, tok.col)
        if tok.type == 'STRING':
            self._advance(); return ('str', tok.value, tok.line, tok.col)
        if tok.type == 'TRUE':
            self._advance(); return ('bool', True, tok.line, tok.col)
        if tok.type == 'FALSE':
            self._advance(); return ('bool', False, tok.line, tok.col)
        if tok.type == 'ID':
            name, line, col = tok.value, tok.line, tok.col
            self._advance()
            if self.cur.type == 'LBRACK':
                self._advance(); idx = self.comparison(); self._eat('RBRACK')
                return ('index', name, idx, line, col)
            if self.cur.type == 'LPAREN':
                self._advance(); args = []
                if self.cur.type != 'RPAREN':
                    args.append(self.comparison())
                    while self.cur.type == 'COMMA':
                        self._advance(); args.append(self.comparison())
                self._eat('RPAREN')
                return ('func_call', name, args, line, col)
            return ('var', name, line, col)
        if tok.type == 'LBRACK':
            line, col = tok.line, tok.col
            self._advance(); elems = []
            if self.cur.type != 'RBRACK':
                elems.append(self.expr())
                while self.cur.type == 'COMMA':
                    self._eat('COMMA'); elems.append(self.expr())
            self._eat('RBRACK')
            return ('array', elems, line, col)
        if tok.type == 'LPAREN':
            self._advance(); node = self.comparison(); self._eat('RPAREN')
            return node
        raise RuntimeError(f"[Line {tok.line}, Col {tok.col}] Unexpected token in factor: {tok}")
