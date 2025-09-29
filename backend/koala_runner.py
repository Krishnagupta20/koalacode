from koalacode.lexer import tokenize
from koalacode.parser import Parser
from koalacode.interpreter import Interpreter
import io
import contextlib
import traceback

def run_koala_code(code: str) -> str:
    output_stream = io.StringIO()

    try:
        with contextlib.redirect_stdout(output_stream):
            # 1. Lexing
            tokens = tokenize(code)

            # 2. Parsing
            parser = Parser(tokens)
            tree = parser.parse()

            if tree is None:
                return "No code to run."

            # 3. Interpreting
            interpreter = Interpreter()
            result = interpreter.eval(tree)   # ✅ use eval instead of visit

    except Exception as e:
        return f"Error: {str(e)}\n{traceback.format_exc(limit=1)}"

    captured = output_stream.getvalue().strip()
    return captured if captured else "No output"
