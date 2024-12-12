from lark.visitors import Visitor
from lark import Tree, Token
import os

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

        if isinstance(children[0], Tree) and children[0].data == 'arg_list':
            params = children[0].children
        else:
            params = [] 

        

        param_types = [(param.children[0].data.replace("_type", ""), param.children[1]) for param in params]

        self.function_table[func_name] = {
            'return_type': return_type,
            'params': param_types
        }
 
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

        func_signature = self.function_table[func_name]


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
        self.symbol_table_stack.pop()
        
    def declare_variable(self, var_name, var_type, value_tree=None):
        current_scope = self.symbol_table_stack[-1]

        current_scope[var_name] = var_type

    def get_variable_type(self, var_name):
        try:
            for scope in reversed(self.symbol_table_stack):
                if var_name in scope:
                    return scope[var_name]
        except:
            raise Exception(f"Variable '{var_name}' not declared")
        
    def reset(self):
        self.symbol_table_stack = [{}]
    

class LLVM_Creator(Visitor):
    def __init__(self, function_table):
        self.instructions = []
        self.variable_index = {}
        self.counter = 0
        self.last_register = None
        self.printable_registers = [] 

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
        operator = tree.children[1]
        right_type = self.eval_expr(tree.children[2])
        if left_type == 'int' and right_type == 'int':
            return 'int'

    def eval_sub_expr(self, tree):
        left_type = self.eval_expr(tree.children[0])
        operator = tree.children[1]
        right_type = self.eval_expr(tree.children[2])
        if left_type == 'int' and right_type == 'int':
            return 'int'

    def eval_mul_expr(self,tree):
        left_type = self.eval_expr(tree.children[0])
        operator = tree.children[1]
        right_type = self.eval_expr(tree.children[2])
        if left_type == 'int' and right_type == 'int':
            return 'int'

    def eval_div_expr(self,tree):
        left_type = self.eval_expr(tree.children[0])
        operator = tree.children[1]
        right_type = self.eval_expr(tree.children[2])
        if left_type == 'int' and right_type == 'int':
            return 'int'

    def eval_and_expr(self, tree):
        left_type = self.eval_expr(tree.children[0])
        right_type = self.eval_expr(tree.children[1])
        if left_type == 'boolean' and right_type == 'boolean':
            return 'boolean'
        
    def eval_or_expr(self, tree):
        left_type = self.eval_expr(tree.children[0])
        right_type = self.eval_expr(tree.children[1])
        if left_type == 'boolean' and right_type == 'boolean':
            return 'boolean'
        
    def eval_rel_expr(self, tree):
        left_type = self.eval_expr(tree.children[0])  
        operator = tree.children[1].data             # <, >, ==, !=
        right_type = self.eval_expr(tree.children[2])  

        return 'boolean'

    def eval_paren_expr(self, tree):
        return self.eval_expr(tree.children[0])

    def block(self, tree):
        self.block_analyzer.enter_block()

        for stmt in tree.children:
            self.visit(stmt) 

        self.block_analyzer.exit_block()

    def func_call_expr(self, tree):
        func_name = tree.children[0].value
        func_signature = self.function_table[func_name]
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
                self.block_analyzer.declare_variable(var_name, var_type.replace("_type", ""))

    def assign_stmt(self, tree):
        var_name = tree.children[0].value
        var_type = self.block_analyzer.get_variable_type(var_name)
        expr = tree.children[1]
        expr_type = self.eval_expr(expr)
        value_reg = None #Na razie nic

        if var_name not in self.variable_index:
            self.instructions.append(f"%{var_name} = alloca i32")
            self.variable_index[var_name] = True

        self.instructions.append(f"store i32 {value_reg}, i32* %{var_name}")


    def variable(self, tree):
        var_name = tree.children[0].value
        var_type = self.block_analyzer.get_variable_type(var_name)
     
    def var_decl_with_expr(self, tree):
        var_type = tree.children[0]
        var_name = tree.children[1].value
        expr = tree.children[2]
        expr_type = self.eval_expr(expr)

        self.block_analyzer.declare_variable(var_name, var_type)

    def topdef(self, tree):
        func_name = tree.children[1].value
        self.current_function = (func_name, False)
        return_type = tree.children[0].data.replace("_type", "")
        block = tree.children[-1]

        if func_name not in self.function_table:
            self.function_table[func_name] = {
                'return_type': return_type,
                'params': []
            }

        self.code_reachable = True
        # self.block_analyzer.enter_block()
        self.visit(block)  # Use visit instead of visit_topdown
        # self.block_analyzer.exit_block()
        self.current_function = (None, False)
        print("Exited function")


    def ret_stmt(self, tree):
        if len(tree.children) > 0:  # Return with a value
            return_expr = tree.children[0]
            return_type = self.eval_expr(return_expr)
        else:  # Return without a value
            return_type = 'void'

        current_function = self.current_function[0]
        expected_type = self.function_table[current_function]['return_type']

        self.code_reachable = False  # Code after a return statement is unreachable


    def if_stmt(self, tree):
        condition = tree.children[0]
        then_block = tree.children[1]

        self.eval_expr(condition)

        previous_reachable = self.code_reachable

        self.visit_topdown(then_block)
        then_reachable = self.code_reachable

        self.code_reachable = previous_reachable

        if len(tree.children) == 3:
            else_block = tree.children[2]
            self.visit_topdown(else_block)
            else_reachable = self.code_reachable

            # Kod po 'if-else' jest osiągalny, jeśli którykolwiek z bloków jest osiągalny
            self.code_reachable = then_reachable or else_reachable
        else:
            # Jeśli nie ma 'else', kod po 'if' jest osiągalny
            self.code_reachable = previous_reachable or then_reachable

    def while_stmt(self, tree):
        condition = tree.children[0]
        body = tree.children[1]
        condition_type = self.eval_expr(condition)
        
        previous_reachable = self.code_reachable
        self.visit(body)
        self.code_reachable = previous_reachable


    def get_instructions(self):
        return self.instructions, self.printable_registers



class LLVM_instructions_MERGER:
    def __init__(self):
        self.printf_decl = 'declare i32 @printf(i8*, ...)\n'
        self.format_str = '@format_str = constant [4 x i8] c"%d\\0A\\00"\n'

        self.start_part = """
define i32 @main() {
entry:
"""

    def create_llvm(self, instructions, printable_registers, filename="TEST"):
        base_filename = os.path.splitext(os.path.basename(filename))[0]
        os.makedirs('foo/bar', exist_ok=True)

        with open(f"foo/bar/{base_filename}.ll", mode='w') as file:
            file.write(self.printf_decl)
            file.write(self.format_str)
            file.write(self.start_part)

            for instruction in instructions:
                file.write(instruction + "\n")
            
            for i, reg in enumerate(printable_registers):
                file.write(f"%fmt_ptr{i} = getelementptr [4 x i8], [4 x i8]* @format_str, i32 0, i32 0\n")
                file.write(f"call i32 (i8*, ...) @printf(i8* %fmt_ptr{i}, i32 {reg})\n")
            
            file.write("ret i32 0\n")
            file.write("}\n")
