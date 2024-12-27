from lark import Lark
from src.LLVM_frontend import *
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

    filename = 'lattests/good/core021.lat'
    code = load_lat(filename)
    print(20*"%",f" Testing {filename} ",20*"%")

    tree, error_msg = parse_code(parser, code)   

    if tree is None:
        print(f"\n\t{error_msg}")
    else:
        try:
            # print(tree.pretty()) 
            SIG_analyzer = SygnatureAnalyzer()   
            SIG_analyzer.visit(tree)
            SIG_analyzer.check_main()
            # SIG_analyzer.display_function_table()
            function_table = SIG_analyzer.function_table
            

            analyzer = SemanticAnalyzer(function_table)
            analyzer.visit(tree) 
            print("\n\nEverything works fine :)")
        except Exception as e:
            print(e)