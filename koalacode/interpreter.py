class RuntimeError_(Exception): 
    pass

class ReturnException(Exception):
    def __init__(self, value): 
        self.value = value


class Interpreter:
    def __init__(self):
        self.env = {}
        self.funcs = {}

    def error(self, message, node=None):
        """Attach line/col info if available."""
        if node and len(node) >= 3:
            line, col = node[-2], node[-1]
            raise RuntimeError_(f"[Line {line}, Col {col}] {message}")
        raise RuntimeError_(message)

    def eval(self, node):
        ntype = node[0]

        if ntype == 'block':
            res = None
            for stmt in node[1]:
                res = self.eval(stmt)
            return res

        if ntype == 'give':
            val = self.eval(node[1])
            print(val)
            return val

        if ntype == 'take':
            return input()

        if ntype == 'if':
            _, cond, then_branch, else_branch, line, col = node
            if self.eval(cond):
                return self.eval(then_branch)
            elif else_branch:
                return self.eval(else_branch)
            return None

        if ntype == 'while':
            _, cond, body, line, col = node
            res = None
            while self.eval(cond):
                res = self.eval(body)
            return res

        if ntype == 'for':
            _, init, cond, step, body, line, col = node
            self.eval(init)
            res = None
            while self.eval(cond):
                res = self.eval(body)
                self.eval(step)
            return res

        if ntype == 'assign':
            _, name, expr, line, col = node
            val = self.eval(expr)
            if name in self.env and type(val) is not type(self.env[name]):
                self.error(
                    f"Type error: {name} was {type(self.env[name]).__name__}, got {type(val).__name__}", 
                    node
                )
            self.env[name] = val
            return val

        if ntype == 'assign_index':
            _, name, idx, val, line, col = node
            if name not in self.env:
                self.error(f"Undefined array {name}", node)
            arr = self.env[name]
            try:
                arr[self.eval(idx)] = self.eval(val)
            except Exception:
                self.error(f"Index out of bounds in array {name}", node)
            return arr

        if ntype == 'expr':
            return self.eval(node[1])

        if ntype == 'binop':
            _, op, left, right, line, col = node
            lval, rval = self.eval(left), self.eval(right)
            try:
                if op == '+': return lval + rval
                if op == '-': return lval - rval
                if op == '*': return lval * rval
                if op == '/': return lval // rval
                if op == '<': return lval < rval
                if op == '>': return lval > rval
                if op == '<=': return lval <= rval
                if op == '>=': return lval >= rval
                if op == '==': return lval == rval
                if op == '!=': return lval != rval
                if op == '!': return not lval
                if op == '&&': return lval and rval
                if op == '||': return lval or rval
            except Exception:
                self.error(f"Invalid operation {op} between {type(lval).__name__} and {type(rval).__name__}", node)
            self.error(f"Unknown operator {op}", node)

        if ntype in ('num','str','bool'):
            return node[1]

        if ntype == 'var':
            name = node[1]
            if name in self.env:
                return self.env[name]
            self.error(f"Undefined variable {name}", node)

        if ntype == 'array':
            return [self.eval(e) for e in node[1]]

        if ntype == 'index':
            _, name, idx, line, col = node
            if name not in self.env:
                self.error(f"Undefined array {name}", node)
            arr = self.env[name]
            index_val = self.eval(idx)
            try:
                return arr[index_val]
            except Exception:
                self.error(f"Index {index_val} out of bounds in array {name}", node)

        if ntype == 'func_def':
            _, name, params, body, line, col = node
            self.funcs[name] = (params, body)
            return None

        if ntype == 'func_call':
            _, name, args, line, col = node
            if name == 'len':
                return len(self.eval(args[0]))
            if name not in self.funcs:
                self.error(f"Undefined function {name}", node)
            params, body = self.funcs[name]
            if len(params) != len(args):
                self.error(f"Function {name} expects {len(params)} args, got {len(args)}", node)

            old_env = self.env.copy()
            self.env.update({p: self.eval(a) for p,a in zip(params,args)})
            try:
                res = self.eval(body)
            except ReturnException as r:
                self.env = old_env
                return r.value
            self.env = old_env
            return res

        if ntype == 'return':
            _, val, line, col = node
            raise ReturnException(self.eval(val))

        self.error(f"Unknown node {ntype}", node)
