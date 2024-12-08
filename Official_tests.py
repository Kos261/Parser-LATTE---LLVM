from lark import Lark, UnexpectedInput, UnexpectedToken, UnexpectedCharacters
from SemanticVisitors import *


def create_bad_test_cases(parser):
    test_cases = []

    test_descriptions = {
        "01":"Pusty program",
        "02":"Tylko litera a?",
        "03":"Dwa razy taki sam argument funkcji",
        "04":"Dwa returny",
        "05":"Brak zwracanego typu funckji",
        "06":"Brak deklaracji typu zmiennej",
        "07":"Dwa razy deklarowana zminenna w bloku",
        "08":"Return nigdy nie osiągnięty przez IF stmt",
        "09":"Przypisanie bool do int",
        "10":"Przez IF stmt zawsze zwracamy zły typ",
        "11":"return int a zwraca bool",
        "12":"Funkcja nic nie zwraca",
        "13":"Złe dodawanie typów",
        "15":"printInt() drukuje int a nie string",
        "16":"printString() drukuje string a nie int",
        "17":"Zła ilośc argumentów podana do foo()",
        "18":"1 argument zamiast dwóch w foo()",
        "19":"2 argumenty zamiast 1 w foo()",
        "20":"Porównanie string i boolean",
        "21":"Każda funkcja (main też) muszi coś zwracać",
        "22":"Przypisanie string do int",
        "23":"Przypisanie int do string",
        "24":"Przez IF stmt nigdy nie ma return",
        "25":"Funkcja f() nigdy nie ma return przez IF stmt",
        "26":"Przypisanie string do int",
        "27":"Przypisanie int do string"
        }

    for test_num, description in test_descriptions.items():
            code = load_ins(f'lattests/bad/bad0{test_num}.lat')
            tree, error_msg = parse_code(parser, code)  # Odbieramy zarówno drzewo, jak i ewentualny błąd
            test_cases.append((description, tree, error_msg, False, test_num))  # Dodajemy error_msg do krotki

    return test_cases

def create_good_test_cases(parser):
    test_cases = []

    test_nums = ['01','02','03','04','05','06','07','08','09','10','11','12','13','14','15','16','17','18','19','20','21','22','23','24','25','26','27','28','31','32','33','34','35']


    
    for test_num in test_nums:
        code = load_ins(f'lattests/good/core0{test_num}.lat')
        tree = parse_code(parser, code)   
        test_cases.append((tree, True, test_num))

    return test_cases

def parse_code(parser, code):
    try:
        tree = parser.parse(code)
        return tree, None  # Zwracamy drzewo i brak błędu
    except (UnexpectedInput, UnexpectedToken, UnexpectedCharacters) as e:
        # Wyciągnij informacje z wyjątku
        line = e.line
        column = e.column
        unexpected = e.get_context(code)
        message = f"Błąd składni w linii {line}, kolumna {column}: {unexpected.strip()[:-2]}"
                                                                    # Wywalam te znaki głupie ^
        return None, message  # Zwracamy brak drzewa i wiadomość o błędzie

def load_ins(filepath):
    program = ""
    with open(filepath, mode='r') as f:
        program = f.read()
    return program




if __name__ == "__main__":
    with open('grammar.lark', 'r', encoding='utf-8') as file:
        grammar = file.read()
    parser = Lark(grammar, parser='lalr', start='start')

    test_cases = create_bad_test_cases(parser)

    passed = 0
    not_passed = 0
    print("%"*30 + " TESTING BAD " + "%"*30)

    for description, test_tree, error_msg, should_pass, test_num in test_cases:
        if test_tree is None and not should_pass:  # Jeśli nie udało się sparsować kodu i tak miało być
            print(f"\n\tPASSED: bad0{test_num} {description} - {error_msg}")
            passed += 1
            continue

        elif test_tree is None and should_pass:  # Jeśli nie udało się sparsować kodu
            print(f"\n\tFAILED: bad0{test_num} {description} - {error_msg}")
            not_passed += 1
            continue

        try:
            SIG_analyzer = SygnatureAnalyzer()
            SIG_analyzer.visit(test_tree)
            function_table = SIG_analyzer.function_table
            analyzer = SemanticAnalyzer(function_table)
            analyzer.visit_topdown(test_tree)
            if not should_pass:
                print(f"\n\tFAILED: bad0{test_num} {description} should fail but passed")
                not_passed += 1
            else:
                print(f"\n\tPASSED: bad0{test_num} {description}")
                passed += 1
                
        except Exception as e:
            if should_pass:
                print(f"\n\tFAILED: bad0{test_num} {description} - {e}")
                not_passed += 1
            else:
                print(f"\n\tPASSED: bad0{test_num} {description} - Caught expected error: {e}")
                passed += 1








    # test_cases = create_good_test_cases(parser)

    # passed = 0
    # not_passed = 0
    # print("%"*30 + "  TESTING GOOD " + "%"*30)
    # for test_tree, should_pass, test_num in test_cases:
    #     try:
    #         SIG_analyzer = SygnatureAnalyzer()
    #         SIG_analyzer.visit(test_tree)
    #         # SIG_analyzer.display_function_table()

    #         function_table = SIG_analyzer.function_table
    #         analyzer = SemanticAnalyzer(function_table)
    #         analyzer.visit_topdown(test_tree)

    #         if not should_pass:
    #             print(f"\n\tFAILED: core0{test_num} should fail but passed")
    #             not_passed += 1
    #         else:
    #             print(f"\n\tPASSED: core0{test_num}")
    #             passed += 1
    #     except Exception as e:
            
    #         if should_pass:
    #             print(f"\n\tFAILED: core0{test_num} - {e}")
    #             not_passed += 1
    #         else:
    #             print(f"\n\tPASSED: bad0{test_num} - Caught expected error: {e}")
    #             passed += 1
    
    
    print("\n")
    print(f"\tPrzeszło {passed}/{passed+not_passed} testów")