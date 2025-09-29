# main.py
import sys
from lexer import tokenize
from parser import Parser
from compiler import Compiler
from vm import VM

def run_code(code):
    tokens = tokenize(code)
    ast = Parser(tokens).parse()
    comp = Compiler()
    comp.compile(ast)
    vm = VM(comp.funcs)
    vm.run(comp.bytecode)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python main.py file.koala")
        sys.exit(1)
    with open(sys.argv[1]) as f:
        run_code(f.read())
