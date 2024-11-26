from lark.visitors import Visitor
from lark import Tree, Token

class SygnatureAnalyzer(Visitor):
    def __init__(self):
        super().__init__()
        self.function_table = {
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
        if func_name in self.function_table:
            raise Exception(f"Function {func_name} is already defined")

        self.function_table[func_name] = {
            'return_type': return_type,
            'params': param_types
        }

    def check_main(self):
        if 'main' not in self.function_table:
            raise Exception('Function "main" is missing')
        
        if self.function_table['main']['return_type'] != 'int':
            raise Exception('Function "main" should return integer')
        
        if self.function_table['main']['params'] != []:
            raise Exception("Function 'main' doesn't allow any arguments")
        
    def display_function_table(self):
        predef = ['printInt', 'printString', 'error', 'readInt', 'readString']
        for func in self.function_table:
            if func not in predef:
                print(f"\n{func} - {self.function_table[func]}")



class FunctionCallAnalyzer(Visitor):
    def __init__(self, function_table, block_analyzer):
        super().__init__()
        self.function_table = function_table
        self.block_analyzer = block_analyzer

    def func_call_expr(self, tree):
        # print("\n\n", tree)
        # print(f"\tChildren of tree: {tree.children}")

        func_name = tree.children[0]

        if len(tree.children[1:]) >= 1:
            args = tree.children[1:][0].children
        else:
            args = []

        # print(f"\nCalling {func_name}")
        # print(f"Arguments: {args}")
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
        print(arg)
        if isinstance(arg, Tree):
            if arg.data == 'int_expr':
                return 'int'
            elif arg.data == 'string_expr':
                return 'string'
            elif arg.data == 'true_expr':
                return 'boolean'
            elif arg.data == 'false_expr':
                return 'boolean'
            elif arg.data == 'var_expr':
                var_name = arg.children[0].value
                try:
                    print("\n\n\tZadeklarowane zmienne\n", self.block_analyzer.symbol_table_stack)
                    return self.block_analyzer.get_variable_type(var_name)
                except Exception:
                    raise Exception(f"Variable {var_name} is not declared")

        raise Exception(f"Unknown type for argument: {arg}")
    


class BlockAnalyzer:
    def __init__(self):
        self.symbol_table_stack = [{}]

    def enter_block(self):
        self.symbol_table_stack.append({})

    def exit_block(self):
        if len(self.symbol_table_stack) > 1:
            self.symbol_table_stack.pop()
        else:
            raise Exception("Attempted to exit global scope")

    def declare_variable(self, var_name, var_type, value_tree=None):
        # print("\nVar declared in Block analyser")
        current_scope = self.symbol_table_stack[-1]

        if var_name in current_scope:
            raise Exception(f"Variable {var_name} already declared in this scope")
        
        if value_tree:
            value_type = self.evaluate_expression(value_tree)
            if value_type != var_type:
                raise Exception(f"Type mismatch: Cannot assign {value_type} to {var_type}")
        
        current_scope[var_name] = var_type
        # print(f"Declared variable {var_name} of type {var_type}")

    def get_variable_type(self, var_name):
        # Sprawdź typ zmiennej w bieżącym zakresie
        for scope in reversed(self.symbol_table_stack):
            if var_name in scope:
                return scope[var_name]
        raise Exception(f"Variable {var_name} not declared")


    def evaluate_expression(self, tree):
        if tree.data == 'int_expr':  # Liczby całkowite
            return 'int'
        
        elif tree.data == 'boolean_expr':  # Wartości logiczne
            return 'boolean'
        
        elif tree.data == 'string_expr':  # Ciągi znaków
            return 'string'
        
        elif tree.data == 'variable':  # Zmienna
            var_name = tree.children[0].value
            return self.get_variable_type(var_name)
        
        elif tree.data == 'add' or tree.data == 'sub':
            left_type = self.evaluate_expression(tree.children[0])
            right_type = self.evaluate_expression(tree.children[1])
            if left_type == 'int' and right_type == 'int':
                return 'int'
            raise Exception(f"Type mismatch in {tree.data}: Cannot use {left_type} and {right_type}")
        
        elif tree.data == 'and' or tree.data == 'or':
            left_type = self.evaluate_expression(tree.children[0])
            right_type = self.evaluate_expression(tree.children[1])
            if left_type == 'boolean' and right_type == 'boolean':
                return 'boolean'
            raise Exception(f"Type mismatch in {tree.data}: Cannot use {left_type} and {right_type}")
        
        else:
            raise Exception(f"Unsupported expression type: {tree.data}")



class SemanticAnalyzer(Visitor):
    def __init__(self, function_table):
        self.function_table = function_table
        self.block_analyzer = BlockAnalyzer()
        self.function_call_analyzer = FunctionCallAnalyzer(self.function_table, self.block_analyzer)


    def eval_expr(self, tree):
        if tree.data == 'int_expr':  
            return 'int'
        
        elif tree.data == 'boolean_expr':  
            return 'boolean'
        
        elif tree.data == 'true_expr' or tree.data == 'false_expr':  # Literalne wartości logiczne
            return 'boolean'

        elif tree.data == 'string_expr':
            return 'string'
        
        elif tree.data == 'variable':  # Zmienna
            var_name = tree.children[0].value
            return self.block_analyzer.get_variable_type(var_name)
        
        elif tree.data == 'add' or tree.data == 'sub':  # Operatory arytmetyczne
            left_type = self.eval_expr(tree.children[0])
            right_type = self.eval_expr(tree.children[1])
            if left_type == 'int' and right_type == 'int':
                return 'int'
            raise Exception(f"Type error: Cannot perform {tree.data} on {left_type} and {right_type}")
        
        elif tree.data == 'and' or tree.data == 'or':  # Operatory logiczne
            left_type = self.eval_expr(tree.children[0])
            right_type = self.eval_expr(tree.children[1])
            if left_type == 'boolean' and right_type == 'boolean':
                return 'boolean'
            raise Exception(f"Type error: Cannot perform {tree.data} on {left_type} and {right_type}")
        
        elif tree.data == 'compare':  # Porównania (np. x > y)
            left_type = self.eval_expr(tree.children[0])
            right_type = self.eval_expr(tree.children[1])
            if left_type == 'int' and right_type == 'int':
                return 'boolean'
            raise Exception(f"Type error: Cannot compare {left_type} and {right_type}")
        
        else:
            raise Exception(f"Unsupported expression type: {tree.data}")

    def block(self, tree):
        self.block_analyzer.enter_block()

        for stmt in tree.children:
            self.visit(stmt)
        
        self.block_analyzer.exit_block()

    def func_decl(self, tree):
        func_name = tree.children[0].value
        return_type = tree.children[1].value
        params = [(param.children.value, param.children[1].value) for param in tree.children[2:-1]]

        if func_name in self.function_table:
            raise Exception(f"Function {func_name} already declared")

        self.function_table[func_name] = {'return_type': return_type, 'params': params}
        # print(f"Declared function {func_name} with params {params}, return type {return_type}")

        self.block_analyzer.enter_block()
        for param_type, param_name in params:
            self.block_analyzer.declare_variable(param_name, param_type)
        self.visit(tree.children[-1])
        self.block_analyzer.exit_block()

    def func_call_expr(self, tree):
        self.function_call_analyzer.func_call_expr(tree)

    def decl_stmt(self, tree):
        
        var_type = tree.children[0].data  
        items = tree.children[1].children  

        default_values = {
            'int_type':Tree('int_expr', [Token('INTEGER', '0')]),
            'boolean_type':Tree('false_expr', []),
            'string_type':Tree('string_expr', [Token('STRING', '""')])
        }

        for item in items:
            var_name = item.children[0].value  
            # int x; albo int x = 10;
            if len(item.children) > 1:
                expr = item.children[1] 
            else:
                expr = default_values[var_type]
            
            expr_type = self.eval_expr(expr)

            #Spr. zgodności typów
            if expr_type != var_type.replace("_type", ""):
                raise Exception(f"Can't assign {expr_type} to {var_type}")

            self.block_analyzer.declare_variable(var_name, var_type.replace("_type", ""))

    def assign_stmt(self, tree):
        var_name = tree.children[0].value
        expr = tree.children[1]

        #Spr. czy zmienna była zadeklarowana
        try:
            var_type = self.block_analyzer.get_variable_type(var_name)
        except Exception as e:
            raise Exception(f"Variable {var_name} is not declared in current scope") from e

        expr_type = self.eval_expr(expr)
        if expr_type != var_type:
            raise Exception(f"Can't assign {expr_type} to {var_type}")

    def variable(self, tree):
        var_name = tree.children[0].value
        var_type = self.block_analyzer.get_variable_type(var_name)
        # print(f"Zmienna {var_name} ma typ {var_type}")

    def var_decl_with_expr(self, tree):
        # print("Var declaring with expression in Semantic analyser")
        var_type = tree.children[0]
        var_name = tree.children[1].value
        expr = tree.children[2]
        # print(f"Declaring variable {var_name} of type {var_type} with expression {expr}")


        expr_type = self.eval_expr(expr)
        # print(f"Evaluated expression type: {expr_type}")


        if expr_type != var_type:
            raise Exception(f"Wrong types: can't assign {expr_type} to {var_type}")
        
        self.block_analyzer.declare_variable(var_name, var_type)

    def add_expr(self, tree):
        left_var = tree.children[0]
        left_type = self.eval_expr(left_var)

        right_var = tree.children[2]
        right_type = self.eval_expr(right_var)

        if left_type != "int" or right_type != "int":
            raise Exception("You can only add 'int'")
    
        return "int"



class ExpressionAnalyzer:
    pass
