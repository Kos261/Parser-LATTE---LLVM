from lark import Lark
from src.LLVM_frontend import *
from src.LLVM_backend import *

def create_test_cases(parser):
    test_cases = []


    try:
        code = load_ins('examples/test01.lat')
        tree = parser.parse(code)   
    except:
        raise Exception(f"Unable to parse 'test01.lat'.")
    test_cases.append(("Duplikacja funkcji (test01)", tree, False))


    try:
        code = load_ins('examples/test02.lat')
        tree = parser.parse(code)   
    except:
        raise Exception("Unable to parse 'test02.lat.")
    test_cases.append(("Zła ilość parametrów (test02)", tree, False))


    try:
        code = load_ins('examples/test03.lat')
        tree = parser.parse(code)   
    except:
        raise Exception("Unable to parse 'test03.lat'.")
    test_cases.append(("Złe przypisanie wartości (test03)", tree, False))


    try:
        code = load_ins('examples/test04.lat')
        tree = parser.parse(code)   
    except:
        raise Exception("Unable to parse 'test04.lat'.")
    test_cases.append(("Niezadeklarowana zmienna (test04)", tree, False))


    try:
        code = load_ins('examples/test05.lat')
        tree = parser.parse(code)   
    except:
        raise Exception("Unable to parse 'test05.lat'.")
    test_cases.append(("Poprawny program (test05)", tree, True))


    try:
        code = load_ins('examples/test06.lat')
        tree = parser.parse(code)   
    except:
        raise Exception("Unable to parse 'test06.lat'.")
    test_cases.append(("Poprawny program (test06)", tree, True))

    return test_cases


def create_test_cases_2(parser):
    test_cases = []


    try:
        code = load_ins('examples/core001block.lat')
        tree = parser.parse(code)   
    except:
        raise Exception(f"Unable to parse 'core001block.lat'.")
    test_cases.append(("Testowanie bloków", tree, True))


    try:
        code = load_ins('examples/core001fac.lat')
        tree = parser.parse(code)   
    except:
        raise Exception("Unable to parse 'core001fac.lat.")
    test_cases.append(("Testowanie funkcji iteracyjnie", tree, True))


    try:
        code = load_ins('examples/core001rfac.lat')
        tree = parser.parse(code)   
    except:
        raise Exception("Unable to parse 'core001rfac.lat'.")
    test_cases.append(("Testowanie funkcji rekurencyjnych", tree, True))


    try:
        code = load_ins('examples/core001repStr.lat')
        tree = parser.parse(code)   
    except:
        raise Exception("Unable to parse 'core001repStr.lat'.")
    test_cases.append(("Testowanie funkcji repStr", tree, True))


    try:
        code = load_ins('examples/core001while.lat')
        tree = parser.parse(code)   
    except:
        raise Exception("Unable to parse 'core001while.lat'.")
    test_cases.append(("Testowanie while", tree, True))

    return test_cases


def load_ins(filepath):
    program = ""
    with open(filepath, mode='r') as f:
        program = f.read()
    return program




if __name__ == "__main__":
    with open('lattests/grammar.lark', 'r', encoding='utf-8') as file:
        grammar = file.read()
    parser = Lark(grammar, parser='lalr', start='start')

    test_cases = create_test_cases_2(parser)
    # test_cases = [test_cases[2]]  #Można odkomentować do testowania konkretnego przypadku

    print("%"*30 + "  TESTING  " + "%"*30)
    for description, test_tree, should_pass in test_cases:
        try:
            SIG_analyzer = SygnatureAnalyzer()
            SIG_analyzer.visit_topdown(test_tree)
            function_table = SIG_analyzer.function_table

            analyzer = SemanticAnalyzer(function_table)
            analyzer.block_analyzer.reset()
            analyzer.visit_topdown(test_tree)


            print(test_tree.pretty()) 
            backend = LLVM_QuadCode(function_table)
            backend.visit(test_tree)
            print("\n\nKOD CZWÓRKOWY")
            for q in backend.quadruples:
                print(q)
            if not should_pass:
                print(f"\n\tFAILED: {description} - should fail but passed")
            else:
                print(f"\n\tPASSED: {description} - no errors")
        except Exception as e:
            if should_pass:
                print(f"\n\tFAILED: {description} - Unexpected error: {e}")
            else:
                print(f"\n\tPASSED: {description} - Caught expected error: {e}")

    print("\n")