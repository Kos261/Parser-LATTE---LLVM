import os
import sys
from lark import Lark, UnexpectedInput, UnexpectedToken, UnexpectedCharacters
from SemanticVisitors import *
from Official_tests import parse_code

def load_lat(filepath):
    program = ""
    with open(filepath, mode='r') as f:
        program = f.read()
    return program



if __name__ == "__main__":
    with open('grammar.lark', 'r', encoding='utf-8') as file:
        grammar = file.read()
    parser = Lark(grammar, parser='lalr', start='start')


    filename = 'examples/simpletests/test08.lat'
    # filename = 'lattests/good/core001.lat'
    code = load_lat(filename)
    print(20*"%",f" Testing {filename} ",20*"%")

    tree, error_msg = parse_code(parser, code)   

    if tree is None:
        print(f"\n\t{error_msg}")
    else:
        # try:
            # print(tree.pretty()) 
            SIG_analyzer = SygnatureAnalyzer()   
            SIG_analyzer.visit(tree)
            SIG_analyzer.check_main()
            function_table = SIG_analyzer.function_table

            analyzer = SemanticAnalyzer(function_table)
            analyzer.visit(tree) 
        # except Exception as e:
        #     print(e)
        #     traceback.pri