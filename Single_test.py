import os
from lark import Lark
from SemanticVisitors import *


def load_lat(filepath):
    program = ""
    with open(filepath, mode='r') as f:
        program = f.read()
    return program



if __name__ == "__main__":
    with open('grammar.lark', 'r', encoding='utf-8') as file:
        grammar = file.read()
    parser = Lark(grammar, parser='lalr', start='start')

    # code = load_lat('lattests/good/core001.lat')
    code = load_lat('examples/simpletests/test07.lat')
    tree = parser.parse(code)   
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