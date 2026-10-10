"""Command-line interface.

    python main.py                      interactive mode
    python main.py examples/basic.math  run a script file
"""
import sys

from errors import MathDSLError
from interpreter import Interpreter
from parser import parse


def run_source(source, interpreter=None):
    """Parse and run a whole program; return the printed lines (raises MathDSLError)."""
    return (interpreter or Interpreter()).run(parse(source))


def run_file(path, out=sys.stdout, err=sys.stderr):
    """Run a .math script. The whole file is parsed first, so a syntax error
    stops everything before any output is produced. Returns an exit code."""
    try:
        with open(path, encoding="utf-8") as f:
            source = f.read()
    except OSError as e:
        print(f"Cannot open '{path}': {e.strerror}", file=err)
        return 1
    try:
        statements = parse(source)
    except MathDSLError as e:
        print(e, file=err)
        return 1
    interpreter = Interpreter()
    for stmt in statements:
        try:
            line = interpreter.execute(stmt)
        except MathDSLError as e:
            print(e, file=err)
            return 1
        if line is not None:
            print(line, file=out)
    return 0


def repl(out=sys.stdout, err=sys.stderr):
    """Interactive mode. Variables persist for the whole session."""
    print("Math DSL - type 'exit' to quit.", file=out)
    interpreter = Interpreter()
    while True:
        try:
            text = input(">>> ")
        except (EOFError, KeyboardInterrupt):
            print(file=out)
            return 0
        if text.strip() in ("exit", "quit"):
            return 0
        try:
            for line in run_source(text, interpreter):
                print(line, file=out)
        except MathDSLError as e:
            print(e.format(show_line=False), file=err)


def main(argv):
    if len(argv) > 2:
        print("Usage: python main.py [script.math]", file=sys.stderr)
        return 2
    return run_file(argv[1]) if len(argv) == 2 else repl()


if __name__ == "__main__":
    sys.exit(main(sys.argv))
