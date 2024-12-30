from lark.visitors import Visitor
from lark import Tree, Token
from src.IRdataclasses import *
from src.LLVM_frontend import BlockAnalyzer, FunctionCallAnalyzer




class LLVM_Creator(Visitor):
    def __init__(self, function_table):
        self.instructions = []
        self.quadruples = []


        self.variable_index = {}
        self.temp_counter = 0
        self.label_counter = 0
        self.register_counter = 0
        self.last_register = None

        self.function_table = function_table
        self.block_analyzer = BlockAnalyzer()
        self.function_call_analyzer = FunctionCallAnalyzer(self.function_table, self.block_analyzer)
        self.current_function = (None, False)

    def new_temp(self) -> str:
        self.temp_counter += 1
        return f"t{self.temp_counter}"

    def new_label(self):
        self.label_counter += 1
        return f"L{self.label_counter}"

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

            'add_expr': self.Binary_expr,
            'sub_expr': self.Binary_expr,
            'mul_expr': self.Binary_expr,
            'div_expr': self.Binary_expr,

            'and_expr':self.Logical_expr,
            'or_expr': self.Logical_expr,
            'not_expr':self.Logical_expr,
            'neg_expr':self.Logical_expr,

            'rel_expr': self.eval_rel_expr,
            'paren_expr': self.eval_paren_expr,
            'func_call_expr': self.func_call_expr,
        }

        if tree.data in handlers:
            return handlers[tree.data](tree)
        else:
            raise Exception(f"Unsupported expression type: {tree.data}")
        
    def eval_int_expr(self, tree):
        value = tree.children[0].value
        return value

    def eval_boolean_expr(self, tree): # To nie jest w ogóle teraz używane?
        value = tree.children[0].value
        return value

    def eval_boolean_literal(self, tree):
        print(f"Processing boolean literal: {tree.data}")
        if tree.data == 'true_expr':
            return 'true'
        elif tree.data == 'false_expr':
            return 'false'
        else:
            raise Exception(f"Nieznany węzeł logiczny: {tree.data}")


    def eval_string_expr(self, tree):
        return 'string'

    def eval_var_expr(self, tree):
        var_name = tree.children[0].value
        return self.block_analyzer.get_variable_type(var_name)

    def eval_add_expr(self, tree):
        return self.Binary_expr(tree)

    def Binary_expr(self, tree):
        print(tree.pretty())
        left_tree = tree.children[0]
        operator = tree.children[1].data
        right_tree = tree.children[2]

        left_result = self.eval_expr(left_tree)
        right_result = self.eval_expr(right_tree)
        result = self.new_temp()

        self.quadruples.append(BinaryOperation(
            operator=operator,
            left=left_result,
            right=right_result,
            result=result
        ))

        return result

    def Logical_expr(self, tree):
        left_tree = tree.children[0]
        right_tree = tree.children[1]

        # Ewaluacja lewej strony
        left_result = self.eval_expr(left_tree)
        result = self.new_temp()

        # Etykiety dla krótkiego spięcia
        false_label = self.new_label()
        end_label = self.new_label()

        # Krótkie spięcie dla AND (&&)
        if tree.data == 'and_expr':
            self.quadruples.append(('if_false', left_result, None, false_label))  # Jeśli lewy operand jest false, przejdź do L1
            right_result = self.eval_expr(right_tree)                             # Ewaluacja prawego operand
            self.quadruples.append(('assign', right_result, None, result))        # Przypisanie wyniku prawego operand do t1
            self.quadruples.append(('goto', None, None, end_label))               # Skok na koniec wyrażenia
            self.quadruples.append((false_label, 'assign', 'false', result))      # Jeśli lewy operand jest false, przypisz false do t1
            self.quadruples.append((end_label, None, None, None))                 # Koniec wyrażenia

        elif tree.data == 'or_expr':
            pass
        return result

       



    def eval_and_expr(self, tree):
        return self.Logical_expr(tree)
        # left_expr = tree.children[0]
        # left_type = self.eval_expr(left_expr)

        # right_expr = tree.children[1]
        # right_type = self.eval_expr(right_expr)
        
        # print("Left and right: ",left_expr, right_expr)


        # instruction = LogicalOperation(
        #     operator='&&',
        #     left=left_expr,
        #     right=right_expr,
        #     result=self.new_temp()
        # )

    def eval_or_expr(self, tree):
        left_type = self.eval_expr(tree.children[0])
        right_type = self.eval_expr(tree.children[1])
        if left_type == 'boolean' and right_type == 'boolean':
            return 'boolean'
       
    def eval_not_expr(self, tree):
        expr = tree.children[0]
        expr_type = self.eval_expr(expr)

        instruction = UnaryOperation(
            operator='~',
            operand=expr,
            result=self.new_temp()
        )

        # Dodajesz do quadruples
        self.quadruples.append(instruction)

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

