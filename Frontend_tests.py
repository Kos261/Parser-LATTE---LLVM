import os
from lark import Lark, Transformer, v_args
from TreeVisitorLLVM import TreeVisitorLLVM
from SemanticVisitors import *


def create_test_cases(parser):
    test_cases = []


    try:
        code = load_ins('examples/simpletests/test01.lat')
        tree = parser.parse(code)   
    except:
        raise Exception(f"Unable to parse 'test01.lat'.")
    test_cases.append(("Duplikacja funkcji", tree, False))


    try:
        code = load_ins('examples/simpletests/test02.lat')
        tree = parser.parse(code)   
    except:
        raise Exception("Unable to parse 'test02.lat.")
    test_cases.append(("Zła ilość parametrów", tree, False))


    # try:
    code = load_ins('examples/simpletests/test03.lat')
    tree = parser.parse(code)   
    # except:
        # raise Exception("Unable to parse 'test03.lat'.")
    test_cases.append(("Złe przypisanie wartości", tree, False))


    try:
        code = load_ins('examples/simpletests/test04.lat')
        tree = parser.parse(code)   
    except:
        raise Exception("Unable to parse 'test04.lat'.")
    test_cases.append(("Niezadeklarowana zmienna", tree, False))


    try:
        code = load_ins('examples/simpletests/test05.lat')
        tree = parser.parse(code)   
    except:
        raise Exception("Unable to parse 'test05.lat'.")
    test_cases.append(("Poprawny program", tree, True))

    return test_cases

def load_ins(filepath):
    program = ""
    with open(filepath, mode='r') as f:
        program = f.read()
    return program




if __name__ == "__main__":
    with open('grammar.lark', 'r', encoding='utf-8') as file:
        grammar = file.read()
    parser = Lark(grammar, parser='lalr', start='start')

    test_cases = create_test_cases(parser)
    # test_cases = [test_cases[2]]




    print("%"*30 + "  TESTING  " + "%"*30)
    for description, test_tree, should_pass in test_cases:
        try:
            SIG_analyzer = SygnatureAnalyzer()
            SIG_analyzer.visit(test_tree)
            # SIG_analyzer.display_function_table()

            function_table = SIG_analyzer.function_table
            analyzer = SemanticAnalyzer(function_table)
            analyzer.visit(test_tree)

            if not should_pass:
                print(f"\n\tFAILED: {description} should fail but passed")
            else:
                print(f"\n\tPASSED: {description}")
        except Exception as e:
            if should_pass:
                print(f"\n\tFAILED: {description} - {e}")
            else:
                print(f"\n\tPASSED: {description} - Caught expected error: {e}")

    print("\n")