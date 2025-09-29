class CompileError(Exception):
    pass


class Compiler:
    def __init__(self):
        self.bytecode = []
        self.funcs = {}

    def emit(self, op, arg=None):
        self.bytecode.append((op, arg))

    def compile(self, node):
        kind = node[0]

        # --- BLOCK ---
        if kind == "block":
            _, stmts, line, col = node
            for stmt in stmts:
                self.compile(stmt)
            return

        # --- GIVE (print) ---
        if kind == "give":
            _, expr, line, col = node
            self.compile(expr)
            self.emit("PRINT")
            return

        # --- TAKE (input) ---
        if kind == "take":
            _, line, col = node
            self.emit("INPUT")
            return

        # --- ASSIGN ---
        if kind == "assign":
            _, name, expr, line, col = node
            self.compile(expr)
            self.emit("STORE_VAR", name)
            return

        # --- ASSIGN TO ARRAY INDEX ---
        if kind == "assign_index":
            _, name, idx, val, line, col = node
            self.compile(idx)
            self.compile(val)
            self.emit("STORE_INDEX", name)
            return

        # --- VARIABLE ---
        if kind == "var":
            _, name, line, col = node
            self.emit("LOAD_VAR", name)
            return

        # --- ARRAY LITERAL ---
        if kind == "array":
            _, elems, line, col = node
            for e in elems:
                self.compile(e)
            self.emit("BUILD_ARRAY", len(elems))
            return

        # --- ARRAY INDEX ---
        if kind == "index":
            _, name, idx, line, col = node
            self.compile(idx)
            self.emit("LOAD_INDEX", name)
            return

        # --- LITERALS ---
        if kind == "num":
            _, val, line, col = node
            self.emit("PUSH_CONST", val)
            return
        if kind == "str":
            _, val, line, col = node
            self.emit("PUSH_CONST", val)
            return
        if kind == "bool":
            _, val, line, col = node
            self.emit("PUSH_CONST", val)
            return

        # --- BINOP ---
        if kind == "binop":
            _, op, left, right, line, col = node
            self.compile(left)
            self.compile(right)
            self.emit("BINARY_OP", op)
            return

        # --- IF ---
        if kind == "if":
            _, cond, then_branch, else_branch, line, col = node
            self.compile(cond)
            jmp_false_pos = len(self.bytecode)
            self.emit("JUMP_IF_FALSE", None)
            self.compile(then_branch)
            if else_branch:
                jmp_end_pos = len(self.bytecode)
                self.emit("JUMP", None)
                self.bytecode[jmp_false_pos] = ("JUMP_IF_FALSE", len(self.bytecode))
                self.compile(else_branch)
                self.bytecode[jmp_end_pos] = ("JUMP", len(self.bytecode))
            else:
                self.bytecode[jmp_false_pos] = ("JUMP_IF_FALSE", len(self.bytecode))
            return

        # --- WHILE ---
        if kind == "while":
            _, cond, body, line, col = node
            loop_start = len(self.bytecode)
            self.compile(cond)
            jmp_false_pos = len(self.bytecode)
            self.emit("JUMP_IF_FALSE", None)
            self.compile(body)
            self.emit("JUMP", loop_start)
            self.bytecode[jmp_false_pos] = ("JUMP_IF_FALSE", len(self.bytecode))
            return

        # --- FOR ---
        if kind == "for":
            _, init, cond, step, body, line, col = node
            self.compile(init)
            loop_start = len(self.bytecode)
            self.compile(cond)
            jmp_false_pos = len(self.bytecode)
            self.emit("JUMP_IF_FALSE", None)
            self.compile(body)
            self.compile(step)
            self.emit("JUMP", loop_start)
            self.bytecode[jmp_false_pos] = ("JUMP_IF_FALSE", len(self.bytecode))
            return

        # --- FUNCTION DEF ---
        if kind == "func_def":
            _, name, params, body, line, col = node
            inner = Compiler()
            inner.compile(body)
            inner.emit("PUSH_CONST", None)  # ensure function returns something
            inner.emit("RETURN")
            self.funcs[name] = (params, inner.bytecode)
            self.emit("MAKE_FUNC", name)
            return

        # --- FUNCTION CALL ---
        if kind == "func_call":
            _, name, args, line, col = node
            for a in args:
                self.compile(a)
            self.emit("CALL_FUNC", (name, len(args)))
            return

        # --- RETURN ---
        if kind == "return":
            _, val, line, col = node
            self.compile(val)
            self.emit("RETURN")
            return

        # --- EXPR WRAPPER ---
        if kind == "expr":
            _, expr, line, col = node
            self.compile(expr)
            self.emit("POP")  # discard result
            return

        raise CompileError(f"Unknown node {kind}")

