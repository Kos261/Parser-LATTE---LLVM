from lark import Lark, UnexpectedToken
from SemanticVisitors import *


def create_test_cases(parser):
    test_cases = []

    test_descriptions = {
        # "01":"Pusty program",
        # "02":"Tylko litera a?",
        "03":"Dwa razy taki sam argument funkcji",
        "04":"Dwa returny",
        # "05":"Brak zwracanego typu funckji",
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
        tree = parse_code(parser, code)   
        test_cases.append((description, tree, False, test_num))

    return test_cases

def parse_code(parser, code):
    try:
        return parser.parse(code)
    except UnexpectedToken as e:
        # Wyciągnij podstawowe informacje o błędzie
        error_line = e.line
        error_column = e.column
        unexpected_token = e.token
        expected_tokens = ', '.join(e.expected)
        
        # Dostosowany komunikat błędu
        message = (f"Błąd składni w linii {error_line}, kolumna {error_column}: "
                   f"nieoczekiwany token '{unexpected_token.value}'. Oczekiwano: {expected_tokens}.")
        raise Exception(message) from e


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



    passed = 0
    not_passed = 0
    print("%"*30 + "  TESTING  " + "%"*30)
    for description, test_tree, should_pass, test_num in test_cases:
        try:
            SIG_analyzer = SygnatureAnalyzer()
            SIG_analyzer.visit(test_tree)
            # SIG_analyzer.display_function_table()

            function_table = SIG_analyzer.function_table
            analyzer = SemanticAnalyzer(function_table)
            analyzer.visit(test_tree)

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
    print("\n")
    print(f"\tPrzeszło {passed}/{passed+not_passed} testów")