import os
from lark import Lark, UnexpectedInput, UnexpectedToken, UnexpectedCharacters
from SemanticVisitors import *


def load_lat(filepath):
    program = ""
    with open(filepath, mode='r') as f:
        program = f.read()
    return program

def parse_code(parser, code):
    try:
        return parser.parse(code)
    except (UnexpectedInput, UnexpectedToken, UnexpectedCharacters) as e:
        # Wyciągnij informacje z wyjątku
        line = e.line
        column = e.column
        unexpected = e.get_context(code)
        message = f"Błąd składni w linii {line}, kolumna {column}: {unexpected.strip()}"
        raise Exception(message) from e


if __name__ == "__main__":
    with open('grammar.lark', 'r', encoding='utf-8') as file:
        grammar = file.read()
    parser = Lark(grammar, parser='lalr', start='start')

    # code = load_lat('lattests/good/core001.lat')
    code = load_lat('examples/simpletests/test07.lat')
    tree = parse_code(parser, code)   
    print(tree.pretty())    

    try:
        SIG_analyzer = SygnatureAnalyzer()   
        SIG_analyzer.visit_topdown(tree)
        SIG_analyzer.check_main()
        function_table = SIG_analyzer.function_table

        analyzer = SemanticAnalyzer(function_table)
        analyzer.visit_topdown(tree) 
    except Exception as e:
        print(e)