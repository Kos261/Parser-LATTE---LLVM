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

    def topdef(self, tree):
        func_name = tree.children[1].value 
        return_type_node = tree.children[0] 
        return_type = return_type_node.data.replace("_type", "")
        children = tree.children[2:]

        # Ustalanie parametrów
        if isinstance(children[0], Tree) and children[0].data == 'arg_list':
            params = children[0].children
        else:
            params = [] 

        if self.check_repeated_params(params):
            raise Exception(f"Repeated parameters in function {func_name}")
        

        param_types = [(param.children[0].data.replace("_type", ""), param.children[1]) for param in params]

        # Zapisanie sygnatury funkcji
        if func_name in self.function_table:
            raise Exception(f"Function {func_name} is already defined")

        self.function_table[func_name] = {
            'return_type': return_type,
            'params': param_types
        }

    def check_repeated_params(self,params):
        params_set = set(params)
        return len(params) != len(params_set)

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
        func_name = tree.children[0]

        if len(tree.children[1:]) >= 1:
            args = tree.children[1:][0].children
        else:
            args = []

        if func_name not in self.function_table:
            raise Exception(f"Undefined function: {func_name}")
        
        func_signature = self.function_table[func_name]
        expected_params = func_signature['params']

        if len(args) != len(expected_params):
            raise Exception(f"{func_name}() expects {len(expected_params)} number of arguments, got {len(args)}")
        
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
            elif arg.data == 'var_expr':
                var_name = arg.children[0].value
                try:
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
        current_scope = self.symbol_table_stack[-1]

        if var_name in current_scope:
            raise Exception(f"Variable {var_name} already declared in this scope")
        
        current_scope[var_name] = var_type
        # print(f"Declared variable '{var_name}' of type '{var_type}' in current scope.")

    def get_variable_type(self, var_name):
        try:
            for scope in reversed(self.symbol_table_stack):
                if var_name in scope:
                    return scope[var_name]
        except:
            raise Exception(f"Variable '{var_name}' not declared")
        
    def reset(self):
        self.symbol_table_stack = [{}]
    

class SemanticAnalyzer(Visitor):
    def __init__(self, function_table):
        self.function_table = function_table
        self.block_analyzer = BlockAnalyzer()
        self.function_call_analyzer = FunctionCallAnalyzer(self.function_table, self.block_analyzer)
        self.current_function = (None, False)
        self.code_reachable = True

    def eval_expr(self, tree):
        handlers = {
            'int_expr': self.eval_int_expr,
            'boolean_expr': self.eval_boolean_expr,
            'true_expr': self.eval_boolean_literal,
            'false_expr': self.eval_boolean_literal,
            'string_expr': self.eval_string_expr,
            'var_expr': self.eval_var_expr,
            'add_expr': self.eval_add_expr,
            'sub_expr': self.eval_sub_expr,
            'and': self.eval_and_expr,
            'mul_expr': self.eval_mul_expr,
            'div_expr': self.eval_div_expr,
            'or': self.eval_or_expr,
            'rel_expr': self.eval_rel_expr,
            'paren_expr': self.eval_paren_expr,
            'func_call_expr': self.func_call_expr,
        }

        if tree.data in handlers:
            return handlers[tree.data](tree)
        else:
            raise Exception(f"Unsupported expression type: {tree.data}")
        
    def eval_int_expr(self, tree):
        return 'int'

    def eval_boolean_expr(self, tree):
        return 'boolean'

    def eval_boolean_literal(self, tree):
        return 'boolean'

    def eval_string_expr(self, tree):
        return 'string'

    def eval_var_expr(self, tree):
        var_name = tree.children[0].value
        return self.block_analyzer.get_variable_type(var_name)

    def eval_add_expr(self, tree):
        left_type = self.eval_expr(tree.children[0])
        operator = tree.children[1]  # plus_op
        right_type = self.eval_expr(tree.children[2])
        if left_type == 'int' and right_type == 'int':
            return 'int'
        raise Exception(f"Type error: Cannot add '{left_type}' and '{right_type}'")

    def eval_sub_expr(self, tree):
        left_type = self.eval_expr(tree.children[0])
        operator = tree.children[1]  # plus_op
        right_type = self.eval_expr(tree.children[2])
        if left_type == 'int' and right_type == 'int':
            return 'int'
        raise Exception(f"Type error: Cannot subtract '{left_type}' and '{right_type}'")

    def eval_mul_expr(self,tree):
        left_type = self.eval_expr(tree.children[0])
        operator = tree.children[1]  # plus_op
        right_type = self.eval_expr(tree.children[2])
        if left_type == 'int' and right_type == 'int':
            return 'int'
        raise Exception(f"Type error: Cannot multiply '{left_type}' and '{right_type}'")

    def eval_div_expr(self,tree):
        left_type = self.eval_expr(tree.children[0])
        operator = tree.children[1]  # plus_op
        right_type = self.eval_expr(tree.children[2])
        if left_type == 'int' and right_type == 'int':
            return 'int'
        raise Exception(f"Type error: Cannot divide '{left_type}' and '{right_type}'")

    def eval_and_expr(self, tree):
        left_type = self.eval_expr(tree.children[0])
        right_type = self.eval_expr(tree.children[1])
        if left_type == 'boolean' and right_type == 'boolean':
            return 'boolean'
        raise Exception(f"Type error: Cannot perform 'and' on '{left_type}' and '{right_type}'")

    def eval_or_expr(self, tree):
        left_type = self.eval_expr(tree.children[0])
        right_type = self.eval_expr(tree.children[1])
        if left_type == 'boolean' and right_type == 'boolean':
            return 'boolean'
        raise Exception(f"Type error: Cannot perform 'or' on '{left_type}' and '{right_type}'")

    def eval_rel_expr(self, tree):
        left_type = self.eval_expr(tree.children[0])  
        operator = tree.children[1].data             # <, >, ==, !=
        right_type = self.eval_expr(tree.children[2])  

        if left_type != right_type:
            raise Exception(f"Type error: Cannot compare '{left_type}' and '{right_type}' with '{operator}'")

        return 'boolean'

    def eval_paren_expr(self, tree):
        return self.eval_expr(tree.children[0])

    def block(self, tree):
        self.block_analyzer.enter_block()
        previous_reachable = self.code_reachable  

        for stmt in tree.children:
            if not self.code_reachable:
                raise Exception("Unreachable code after return statement")
            self.visit(stmt)
            if self.check_returns(stmt):
                self.code_reachable = False

        self.block_analyzer.exit_block()
        self.code_reachable = previous_reachable

    def func_call_expr(self, tree):
        func_name = tree.children[0].value
        args = tree.children[1].children if len(tree.children) > 1 else []

        if func_name not in self.function_table:
            raise Exception(f"Function '{func_name}' is not declared")

        func_signature = self.function_table[func_name]
        expected_params = func_signature['params']

        if len(args) != len(expected_params):
            raise Exception(f"Function '{func_name}' expects {len(expected_params)} arguments, but got {len(args)}")

        for i, (arg, (expected_type, _)) in enumerate(zip(args, expected_params)):
            arg_type = self.eval_expr(arg)
            if arg_type != expected_type:
                raise Exception(
                    f"Argument {i+1} of function '{func_name}' has incorrect type: "
                    f"expected '{expected_type}', got '{arg_type}'"
                )

        return func_signature['return_type']

    def decl_stmt(self, tree):
        var_type = tree.children[0].data  
        items = tree.children[1].children  

        default_values = {
            'int_type': Tree('int_expr', [Token('INTEGER', '0')]),
            'boolean_type': Tree('false_expr', []),
            'string_type': Tree('string_expr', [Token('STRING', '""')])
        }

        for item in items:
            var_name = item.children[0].value  
            # int x; albo int x = 10;
            if len(item.children) > 1:
                expr = item.children[1] 
            else:
                expr = default_values[var_type]
            
            expr_type = self.eval_expr(expr)

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
     
    def var_decl_with_expr(self, tree):
        var_type = tree.children[0]
        var_name = tree.children[1].value
        expr = tree.children[2]
        expr_type = self.eval_expr(expr)

        if expr_type != var_type:
            raise Exception(f"Wrong types: can't assign {expr_type} to {var_type}")
        
        self.block_analyzer.declare_variable(var_name, var_type)

    def topdef(self, tree):
        func_name = tree.children[1].value
        self.current_function = (func_name, False)
        print("NAzwa funkcji: ",func_name)
        return_type = tree.children[0].data.replace("_type", "")
        block = tree.children[-1]

        if func_name not in self.function_table:
            self.function_table[func_name] = {
                'return_type': return_type,
                'params': []
            }

        print("Kod osiągalny: ",self.code_reachable)
        self.code_reachable = True
        self.block_analyzer.enter_block()
        self.visit(block)
        self.block_analyzer.exit_block()

        # Spr. if branches
        if return_type != "void":
            if not self.check_returns(block):
                raise Exception(f"Function '{func_name}' may not return a value of type '{return_type}' on all paths")

        self.current_function = (None, False)

    def ret_stmt(self, tree):
        if self.current_function[0] is None:
            raise Exception("Return statement found outside of any function")

        print("KOD RET_STMT NIEOSIĄGALNY",self.code_reachable)
        if not self.code_reachable:
            raise Exception("Unreachable code detected")

        if len(tree.children) > 0:
            return_expr = tree.children[0]
            return_type = self.eval_expr(return_expr)
        else:
            return_type = 'void'

        current_function = self.current_function[0]
        expected_type = self.function_table[current_function]['return_type']

        if return_type != expected_type:
            raise Exception(
                f"Return type mismatch in function '{current_function}': "
                f"expected '{expected_type}', got '{return_type}'"
            )
        
        self.code_reachable = False

    def stmt(self, tree):
        print("STMT KOD NIEOSIĄGALNY", self.code_reachable)
        if not self.code_reachable:
            raise Exception("Unreachable code detected")

        self.visit_topdown(tree.children[0])

    def if_stmt(self, tree):
        condition = tree.children[0]
        then_block = tree.children[1]

        self.eval_expr(condition)

        previous_reachable = self.code_reachable

        self.visit(then_block)
        then_reachable = self.code_reachable

        self.code_reachable = previous_reachable

        if len(tree.children) == 3:
            else_block = tree.children[2]
            self.visit(else_block)
            else_reachable = self.code_reachable
            self.code_reachable = then_reachable or else_reachable
        else:
            self.code_reachable = then_reachable or previous_reachable

    def check_returns(self, tree):
        if isinstance(tree, Tree):
            if tree.data == 'block':
                for stmt in tree.children:
                    if self.check_returns(stmt):
                        return True
                return False
            elif tree.data == 'stmt':
                return self.check_returns(tree.children[0])
            elif tree.data == 'ret_stmt':
                return True
            elif tree.data == 'if_stmt':
                if len(tree.children) == 2:
                    # if bez else – może nie zwrócić
                    return False
                elif len(tree.children) == 3:
                    # if z else – obie gałęzie muszą zwracać
                    then_returns = self.check_returns(tree.children[1])
                    else_returns = self.check_returns(tree.children[2])
                    return then_returns and else_returns
            else:
                for child in tree.children:
                    if self.check_returns(child):
                        return True
                return False
        else:
            return False
