from interpreter.lexer import Lexer
from interpreter.analyser import Analyser
from interpreter.ast.executor import Executor, ASTJsonBuilder
from interpreter.ast.symbol import SymbolTableBuilder

import argparse

def main():
    parser = argparse.ArgumentParser(
        description='SPI - Simple Pascal Interpreter'
    )
    parser.add_argument('inputfile', help='Pascal source file')
    parser.add_argument(
        '--scope',
        help='Print scope information',
        action='store_true',
    )
    parser.add_argument(
        '--stack',
        help='Print call stack',
        action='store_true',
    )
    args = parser.parse_args()

    with open(args.inputfile, "r") as f :
        text = f.read()
        lexer = Lexer(text)
        analyser = Analyser(lexer)
        ast = analyser.parse()
        executor = Executor(ast)
        symtab_builder = SymbolTableBuilder(ast)

        print(symtab_builder.run())
        # executor.run()

if __name__ == '__main__':
    main()
