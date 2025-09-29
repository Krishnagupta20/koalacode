class VM:
    def __init__(self, funcs=None):
        self.stack = []
        self.vars = {}
        self.ip = 0
        self.code = []
        self.funcs = funcs or {}
        self.call_stack = []

    def run(self, code):
        self.code = code
        self.ip = 0
        while self.ip < len(self.code):
            instr, arg = self.code[self.ip]
            self.ip += 1

            if instr == "PUSH_CONST":
                self.stack.append(arg)

            elif instr == "POP":
                self.stack.pop()

            elif instr == "LOAD_VAR":
                self.stack.append(self.vars[arg])

            elif instr == "STORE_VAR":
                self.vars[arg] = self.stack.pop()

            elif instr == "BUILD_ARRAY":
                n = arg
                arr = self.stack[-n:]
                self.stack = self.stack[:-n]
                self.stack.append(arr)

            elif instr == "LOAD_INDEX":
                idx = self.stack.pop()
                arr = self.vars[arg]
                self.stack.append(arr[idx])

            elif instr == "STORE_INDEX":
                val = self.stack.pop()
                idx = self.stack.pop()
                self.vars[arg][idx] = val

            elif instr == "PRINT":
                print(self.stack.pop())

            elif instr == "INPUT":
                self.stack.append(input())

            elif instr == "BINARY_OP":
                b = self.stack.pop()
                a = self.stack.pop()
                op = arg
                if op == "+": self.stack.append(a + b)
                elif op == "-": self.stack.append(a - b)
                elif op == "*": self.stack.append(a * b)
                elif op == "/": self.stack.append(a // b)
                elif op == "<": self.stack.append(a < b)
                elif op == ">": self.stack.append(a > b)
                elif op == "<=": self.stack.append(a <= b)
                elif op == ">=": self.stack.append(a >= b)
                elif op == "==": self.stack.append(a == b)
                elif op == "!=": self.stack.append(a != b)
                elif op == "&&": self.stack.append(a and b)
                elif op == "||": self.stack.append(a or b)
                else:
                    raise RuntimeError(f"Unknown binary operator {op}")

            elif instr == "JUMP":
                self.ip = arg

            elif instr == "JUMP_IF_FALSE":
                cond = self.stack.pop()
                if not cond:
                    self.ip = arg

            elif instr == "MAKE_FUNC":
                # functions are already compiled in compiler.funcs
                pass

            elif instr == "CALL_FUNC":
                name, argc = arg
                args = [self.stack.pop() for _ in range(argc)][::-1]

                if name == "len":
                    self.stack.append(len(args[0]))
                    continue

                if name not in self.funcs:
                    raise RuntimeError(f"Undefined function {name}")

                params, body = self.funcs[name]

                if len(params) != len(args):
                    raise RuntimeError(f"Function {name} expects {len(params)} args, got {len(args)}")

                # Save current state
                self.call_stack.append((self.ip, self.vars.copy(), self.code))

                # Setup new frame
                self.vars = dict(zip(params, args))
                self.code = body
                self.ip = 0

            elif instr == "RETURN":
                retval = self.stack.pop()
                self.ip, self.vars, self.code = self.call_stack.pop()
                self.stack.append(retval)

            else:
                raise RuntimeError(f"Bad instruction {instr}")
