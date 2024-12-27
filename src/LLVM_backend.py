from lark.visitors import Visitor
from lark import Tree, Token
import os
from src.IRdataclasses import *
from src.LLVM_frontend import BlockAnalyzer, FunctionCallAnalyzer




class LLVM_Creator(Visitor):
    def __init__(self, function_table):
        self.instructions = []
        self.variable_index = {}
        self.counter = 0
        self.last_register = None

        self.function_table = function_table
        self.block_analyzer = BlockAnalyzer()
        self.function_call_analyzer = FunctionCallAnalyzer(self.function_table, self.block_analyzer)
        self.current_function = (None, False)


    def visit(self, tree):
        handlers = {
            'topdef': self.topdef,
            'ret_stmt': self.ret_stmt,
            'vret_stmt': self.vret_stmt,
            'if_stmt': self.if_stmt,
            'if_else_stmt': self.if_else_stmt,
            'while_stmt': self.while_stmt,
            'variable':self.variable,
            'decl_stmt':self.decl_stmt,
            'assign_stmt':self.assign_stmt,
            'block':self.block,
            # Ogólny handler dla wyrażeń
            'int_expr': self.eval_expr,
            'boolean_expr': self.eval_expr,
            'true_expr': self.eval_expr,
            'false_expr': self.eval_expr,
            'string_expr': self.eval_expr,
            'var_expr': self.eval_expr,
            'add_expr': self.eval_expr,
            'sub_expr': self.eval_expr,
            'and_expr': self.eval_expr,
            'or_expr': self.eval_expr,
            'not_expr': self.eval_expr,
            'mul_expr': self.eval_expr,
            'div_expr': self.eval_expr,
            'rel_expr': self.eval_expr,
            'paren_expr': self.eval_expr,
            'func_call_expr': self.eval_expr,
            'decr_stmt': self.decr_stmt,
            'incr_stmt': self.incr_stmt,
            'neg_expr': self.eval_expr,
        }


        # Węzły, które wymagają odwiedzenia poddrzew
        passthrough_nodes = {'start', 'program', 'stmt', 'stmt_list', 'expr_list', 'expr_stmt'}

        # Obsługa węzłów z dedykowaną logiką
        if tree.data in handlers:
            return handlers[tree.data](tree)

        # Jeśli węzeł wymaga odwiedzenia poddrzew, przejdź przez dzieci
        elif tree.data in passthrough_nodes:
            for child in tree.children:
                if isinstance(child, Tree):
                    self.visit(child)

        else:
            raise Exception(f"Unhandled node type: {tree.data}")

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
            'and_expr': self.eval_and_expr,
            'or_expr': self.eval_or_expr,
            'not_expr': self.eval_not_expr,
            'mul_expr': self.eval_mul_expr,
            'div_expr': self.eval_div_expr,
            'rel_expr': self.eval_rel_expr,
            'paren_expr': self.eval_paren_expr,
            'func_call_expr': self.func_call_expr,
            'neg_expr': self.neg_expr,
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
        operator = tree.children[1]
        right_type = self.eval_expr(tree.children[2])

        if left_type == 'int' and right_type == 'int':
            return 'int'
        if left_type == 'string' and right_type == 'string':
            return 'string'

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
       
    def eval_not_expr(self, tree):
        expr = tree.children[0]
        expr_type = self.eval_expr(expr)
        return 'boolean'

    def eval_rel_expr(self, tree):
        left_type = self.eval_expr(tree.children[0])  
        operator = tree.children[1].data             # <, >, ==, !=
        right_type = self.eval_expr(tree.children[2])  

        return 'boolean'

    def eval_paren_expr(self, tree):
        return self.eval_expr(tree.children[0])

    def func_call_expr(self, tree):
        func_name = tree.children[0].value
        args = tree.children[1].children if len(tree.children) > 1 else []

        func_signature = self.function_table[func_name]
        expected_params = func_signature['params']

        return func_signature['return_type']

    def block(self, tree):
        self.block_analyzer.enter_block()

        for stmt in tree.children:  
            self.visit(stmt) 

        self.block_analyzer.exit_block()


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
     
    def decr_stmt(self, tree):
        var_name = tree.children[0].value
        var_type = self.block_analyzer.get_variable_type(var_name)
        

    def incr_stmt(self, tree):
        var_name = tree.children[0].value
        var_type = self.block_analyzer.get_variable_type(var_name)
        
        
    def neg_expr(self, tree):
        expr = tree.children[0]
        expr_type = self.eval_expr(expr)

        return 'int'

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

        # Pobierz parametry funkcji z tabeli funkcji
        params = self.function_table[func_name]['params']
        if func_name not in self.function_table:
            self.function_table[func_name] = {
                'return_type': return_type,
                'params': params
            }

        self.block_analyzer.enter_block()

        for param_type, param_name in params:
            self.block_analyzer.declare_variable(param_name, param_type)

        self.visit(block)

        # Wyjdź z bloku funkcji
        self.block_analyzer.exit_block()
        self.current_function = (None, False)

    def ret_stmt(self, tree):
        if len(tree.children) > 0:  # Return with a value
            return_expr = tree.children[0]
            return_type = self.eval_expr(return_expr)
        else:
            return_type = 'void'

        current_function = self.current_function[0]
        expected_type = self.function_table[current_function]['return_type']
        

    def vret_stmt(self, tree):
        self.ret_stmt(tree)

    def if_stmt(self, tree):
        condition = tree.children[0]
        then_block = tree.children[1]

        self.eval_expr(condition)
        self.visit(then_block)

        if len(tree.children) == 3:
            else_block = tree.children[2]
            self.visit(else_block)
    
        else:
            pass

    def if_else_stmt(self, tree):
        condition = tree.children[0]  # Warunek (rel_expr)
        then_block = tree.children[1]  # Blok 'then'
        else_block = tree.children[2]  # Blok 'else'

        self.eval_expr(condition)

        self.visit(then_block)
        self.visit(else_block)


    def while_stmt(self, tree):
        condition = tree.children[0]
        body = tree.children[1]
        condition_type = self.eval_expr(condition)

        self.visit(body)



    def get_instructions(self):
        return self.instructions

