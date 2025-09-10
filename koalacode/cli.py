# koalacode/cli.py
import sys
from .lexer import tokenize
from .parser import Parser
from .interpreter import Interpreter, RuntimeError_

def run_code(code, interp):
    """Tokenize, parse, and evaluate KoalaCode source code."""
    try:
        tokens = tokenize(code)
        parser = Parser(tokens)
        ast = parser.parse()
        return interp.eval(ast)
    except RuntimeError_ as e:
        print("Runtime Error:", e)
    except Exception as e:
        print("Internal Error:", e)

def main():
    interp = Interpreter()

    # Run from file
    if len(sys.argv) > 1:
        path = sys.argv[1]
        with open(path, "r", encoding="utf-8") as f:
            code = f.read()
        run_code(code, interp)
        return

    # REPL mode
    print("KoalaCode REPL. End with ';' or '}'. Ctrl-C to exit.")
    buf = ""
    while True:
        try:
            line = input("koalacode>>> ")
        except KeyboardInterrupt:
            print("\nExiting KoalaCode.")
            break

        buf += line + "\n"
        if line.strip().endswith(";") or line.strip().endswith("}"):
            run_code(buf, interp)
            buf = ""
