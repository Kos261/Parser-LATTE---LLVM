from lark.visitors import Visitor
from lark import Tree, Token

class SygnatureAnalyzer(Visitor):
    def __init__(self):
        super().__init__()
        self.func_table = {
            'printInt': {'return_type': 'void', 'params': [('int', Token('IDENT', 'a'))]},
            'printString': {'return_type': 'void', 'params': [('string', Token('IDENT', 'a'))]},
            'error': {'return_type': 'void', 'params': []},
            'readInt': {'return_type': 'int', 'params': []},
            'readString': {'return_type': 'string', 'params': []}
        }

        # void printInt(int)
        # void printString(string)
        # void error()
        # int readInt()
        # string readString()

    def topdef(self, tree):
        func_name = tree.children[1]  
        return_type_node = tree.children[0] 
        return_type = return_type_node.data.replace("_type", "")
        children = tree.children[2:]

        # Ustalanie parametrów
        if isinstance(children[0], Tree) and children[0].data == 'arg_list':
            params = children[0].children
            block = children[1]
        else:
            params = []  # Funkcja bez parametrów
            block = children[0]

        param_types = [(param.children[0].data.replace("_type", ""), param.children[1]) for param in params]

        # Zapisanie sygnatury funkcji
        if func_name in self.func_table:
            raise Exception(f"Function {func_name} is already defined")

        self.func_table[func_name] = {
            'return_type': return_type,
            'params': param_types
        }

    def check_main(self):
        if 'main' not in self.func_table:
            raise Exception('Function "main" is missing')
        
        if self.func_table['main']['return_type'] != 'int':
            raise Exception('Function "main" should return integer')
        
        if self.func_table['main']['params'] != []:
            raise Exception("Function 'main' doesn't allow any arguments")
        
        print("Everything is good with main")
        
    def display_function_table(self):
        predef = ['printInt', 'printString', 'error', 'readInt', 'readString']
        for func in self.func_table:
            if func not in predef:
                print(f"\n{func} - {self.func_table[func]}")



class FunctionCallAnalyzer(Visitor):
    def __init__(self, function_table):
        super().__init__()
        self.function_table = function_table



    def func_call_expr(self, tree):
        
        func_name = tree.children[0]
        args = tree.children[1:][0].children
        

        print(f"\nCalling {func_name}")
        print(f"Arguments: {args}")
        # print(f"Number of args: {len(args)}")

        if func_name not in self.function_table:
            raise Exception(f"Undefined function: {func_name}")
        
        func_signature = self.function_table[func_name]
        expected_params = func_signature['params']

        if len(args) != len(expected_params):
            raise Exception(f"\nFunction {func_name} expects {len(expected_params)} number of arguments, got {len(args)}")
        
        
        for i, (arg, (expected_type, _)) in enumerate(zip(args, expected_params)):
            if not self.check_type(arg, expected_type):
                raise Exception(f"\nArgument {i+1} of {func_name} has incorrect type")
            
        


    def check_type(self, arg, expected_type):
        actual_type = self.get_arg_type(arg)
        return actual_type == expected_type

    def get_arg_type(self, arg):
        if isinstance(arg, Tree):
            if arg.data == 'int_expr':
                return 'int'
            elif arg.data == 'string_expr':
                return 'string'
            elif arg.data == 'true_expr':
                return 'boolean'
            elif arg.data == 'false_expr':
                return 'boolean'
        raise Exception(f"Unknown type for argument: {arg}")
    


class BlockAnalyzer:
    def __init__(self):
        self.symbol_table_stack = [{}]  # Stos tabel symboli (jedna tabela na zakres)

    def enter_block(self):
        # Wchodzimy w nowy blok - nowa tabela symboli
        self.symbol_table_stack.append({})

    def exit_block(self):
        # Wychodzimy z bloku - usuwamy ostatnią tabelę symboli
        if len(self.symbol_table_stack) > 1:
            self.symbol_table_stack.pop()
        else:
            raise Exception("Attempted to exit global scope")

    def declare_variable(self, var_name, var_type):
        # Dodaj zmienną do bieżącego zakresu
        current_scope = self.symbol_table_stack[-1]
        if var_name in current_scope:
            raise Exception(f"Variable {var_name} already declared in this scope")
        current_scope[var_name] = var_type
        print(f"Declared variable {var_name} of type {var_type}")

    def get_variable_type(self, var_name):
        # Sprawdź typ zmiennej w bieżącym zakresie
        for scope in reversed(self.symbol_table_stack):
            if var_name in scope:
                return scope[var_name]
        raise Exception(f"Variable {var_name} not declared")



class ExpressionAnalyzer:
    pass